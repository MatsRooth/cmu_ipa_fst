#!/usr/bin/env python3
"""Convert Phonetisaurus aligned lexicons into portable, unweighted ATT tries.

No third-party dependencies. Every chunk is atomic on each relation tape.
Multi-phone chunks retain | separators; orthographic chunks lose them.
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
EPS = '@0@'
IPA = dict(zip(
    'AA AE AH AO AW AY B CH D DH EH ER EY F G HH IH IY JH K L M N NG OW OY P R S SH T TH UH UW V W Y Z ZH'.split(),
    'ɑ æ ʌ ɔ aʊ aɪ b tʃ d ð ɛ ɹ̩ eɪ f ɡ h ɪ i dʒ k l m n ŋ oʊ ɔɪ p ɹ s ʃ t θ ʊ u v w j z ʒ'.split()))
VOWELS = set('AA AE AH AO AW AY EH ER EY IH IY OW OY UH UW'.split())


def phone(token, alphabet, stress):
    base = token.rstrip('012')
    digit = token[len(base):]
    if base not in IPA or (digit and (base not in VOWELS or digit not in ('0', '1', '2'))):
        raise ValueError(f'unknown CMU phone {token!r}')
    if alphabet == 'cmu':
        return token if stress == 'keep' else base
    # Stress-aware schwa; AH2 retains the full vowel convention used for AH1.
    value = 'ə' if token == 'AH0' else IPA[base]
    return value + (digit if stress == 'keep' else '')


def label(value):
    if any(c.isspace() for c in value) or not value:
        raise ValueError(f'invalid ATT symbol {value!r}')
    return value


class Trie:
    def __init__(self):
        self.arcs = [{}]
        self.finals = set()

    def add(self, pairs):
        state = 0
        for upper, lower in pairs:
            pair = (label(upper), label(lower))
            target = self.arcs[state].get(pair)
            if target is None:
                target = len(self.arcs)
                self.arcs[state][pair] = target
                self.arcs.append({})
            state = target
        self.finals.add(state)

    def write(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name + '.tmp')
        with temporary.open('w', encoding='utf-8', newline='\n') as out:
            for state, arcs in enumerate(self.arcs):
                for (upper, lower), target in sorted(arcs.items()):
                    out.write(f'{state}\t{target}\t{upper}\t{lower}\n')
            for state in sorted(self.finals):
                out.write(f'{state}\n')
        temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', type=Path, default=ROOT / 'data/cmudict.aligned')
    parser.add_argument('--phones', choices=('cmu', 'ipa'), default='ipa')
    parser.add_argument('--stress', choices=('keep', 'strip'), default='keep')
    parser.add_argument('--null-cmu', default='NULL')
    parser.add_argument('--null-ipa', default='NULL')
    parser.add_argument('--null', help='override the selected alphabet\'s null label')
    parser.add_argument('--epsilon', action='store_true', help='true epsilon in relation; EPS placeholder in encoded languages')
    parser.add_argument('--representation', choices=('relation', 'interleaved', 'pairs'), default='relation')
    parser.add_argument('--output', type=Path, help='default: data/english-PHONES-REPRESENTATION.att')
    parser.add_argument('--orthographic-output', type=Path, default=ROOT / 'data/orthographic_chunk.att')
    parser.add_argument('--no-orthographic', action='store_true')
    parser.add_argument('--phonetic-output', type=Path, default=ROOT / 'data/phonetic_chunk.att')
    parser.add_argument('--no-phonetic', action='store_true')
    args = parser.parse_args()
    null = args.null or (args.null_cmu if args.phones == 'cmu' else args.null_ipa)
    try:
        label(null)
        if null in (EPS, '@_EPSILON_SYMBOL_@', '@_IDENTITY_SYMBOL_@', '@_UNKNOWN_SYMBOL_@'):
            raise ValueError('reserved null label; use --epsilon for true epsilon')
        net = Trie()
        chunks = set()
        phonetic_chunks = set()
        count = 0
        with args.input.open(encoding='utf-8') as source:
            for number, line in enumerate(source, 1):
                if not line.strip():
                    continue
                alignment = []
                try:
                    for item in line.split():
                        if item.count('}') != 1:
                            raise ValueError(f'expected orthography}}phones, got {item!r}')
                        upper, lower = item.split('}')
                        letters = tuple(upper.split('|')) if upper != '_' else ()
                        if any(len(c) != 1 for c in letters):
                            raise ValueError(f'expected single characters separated by |: {upper!r}')
                        chunk = ''.join(letters)
                        if chunk == null:
                            raise ValueError('orthographic chunk collides with null label')
                        chunks.add(letters)
                        upper_label = chunk or (EPS if args.epsilon and args.representation == 'relation' else null)
                        phones = lower.split('|') if lower != '_' else []
                        if phones:
                            expanded = tuple(phone(p, args.phones, args.stress) for p in phones)
                            phonetic_chunks.add(expanded)
                            lower_label = '|'.join(expanded)
                            if lower_label == null:
                                raise ValueError('phonetic chunk collides with null label')
                        else:
                            phonetic_chunks.add(())
                            lower_label = EPS if args.epsilon and args.representation == 'relation' else null
                        if not letters and not phones:
                            raise ValueError('both sides of a chunk are null')
                        alignment.append((upper_label, lower_label))
                except ValueError as error:
                    raise ValueError(f'{args.input}:{number}: {error}') from error
                if args.representation == 'relation':
                    path = alignment
                elif args.representation == 'interleaved':
                    path = [(s, s) for pair in alignment for s in pair]
                else:
                    path = [(u + '}' + l, u + '}' + l) for u, l in alignment]
                net.add(path)
                count += 1
        orth = Trie()
        for letters in sorted(chunks):
            chunk = ''.join(letters)
            if not letters:
                # Lookup relation already has epsilon on this side when requested.
                if not args.epsilon:
                    orth.add([(EPS, null)])
            else:
                orth.add([(c, chunk if i == len(letters)-1 else EPS) for i, c in enumerate(letters)])
        phonetic = Trie()
        for expanded in sorted(phonetic_chunks):
            if expanded:
                chunk = '|'.join(expanded)
                phonetic.add([(chunk if i == 0 else EPS, p) for i, p in enumerate(expanded)])
            elif not args.epsilon or args.representation != 'relation':
                phonetic.add([(null, EPS)])
        output = args.output or ROOT / f'data/english-{args.phones}-{args.representation}.att'
        net.write(output)
        if not args.no_orthographic:
            orth.write(args.orthographic_output)
        if not args.no_phonetic:
            phonetic.write(args.phonetic_output)
        print(f'{output}: {count} alignments, {len(net.arcs)} states, {len(chunks)} orthographic chunks', file=sys.stderr)
    except (ValueError, OSError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
