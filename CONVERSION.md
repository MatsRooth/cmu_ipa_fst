# Building the aligned dictionaries

Run `./script/build.sh` (Python 3, standard library only). It builds eight
unweighted ATT dictionaries in `data/`: CMU and IPA versions of `relation`,
`interleaved`, `pairs`, and an `epsilon` relation. It also writes
`data/orthographic_chunk.att`. Paths are relative to the script's project,
so the build works from any current directory. Set `PYTHON` to select Python.

Input: `data/cmudict.aligned`, one Phonetisaurus alignment per line. Within a
chunk, `|` separates characters or phones; `}` separates the two sides; `_`
is a null. Orthographic `n|g` becomes the atomic symbol `ng`. Multi-phone
chunks retain `|`, e.g. `Y|UW1` becomes atomic `j|u1`, preserving boundaries.
No trained model is required. Duplicate alignments are coalesced by a trie;
alternative alignments remain distinct. The output is not minimized.

```
python3 script/aligned_to_att.py --phones ipa --representation relation
python3 script/aligned_to_att.py --phones cmu --null-cmu _ --output data/custom.att
python3 script/aligned_to_att.py --phones ipa --stress strip --no-orthographic --output data/ipa-no-stress.att
```

Defaults preserve stress as an ASCII suffix on an atomic vowel symbol:
EY1 -> eɪ1. AH0 -> ə0; AH1/AH2 -> ʌ1/ʌ2. ER -> syllabic ɹ̩; vowels have no
length marks. These are broad transcription conventions, not syllabified IPA.
`--stress strip` removes the suffix after choosing the stress-sensitive vowel.
The mapping is explicit in the Python source and uses the correspondences in
https://github.com/matthewmorrone/cmudict-ipa/blob/master/ipa.tsv as a reference,
with the AH0 refinement above.

Representations of `n|g}NG e}_` in IPA:

* relation: ng:ŋ e:NULL
* interleaved: ng ŋ e NULL (identity automaton)
* pairs: ng}ŋ e}NULL (two atomic symbols in an identity automaton)

`--null-cmu` and `--null-ipa` default to `NULL`; `--null` overrides the selected
one. They control nulls on both tapes. `--epsilon` uses actual epsilon in a
relation. Encoded languages always retain an ordinary null placeholder.
ATT epsilon is `@0@`; no headers, symbol quoting, or weights are emitted.

Orthographic chunk output maps character sequences to single chunk symbols,
including epsilon -> NULL. Compute its Kleene+ to tokenize entire spellings;
compose on the left of the matching relation dictionary. Different null-label
choices require matching chunk maps: use `--orthographic-output` to save them
separately. With `--epsilon`, the chunk map omits epsilon -> NULL. Arbitrary null
insertions in the default chunk closure are filtered by dictionary composition.

Foma:

```
set att-epsilon @0@
read att data/orthographic_chunk.att
define OrthographicChunk
define Orthography OrthographicChunk+;
read att data/english-ipa-relation.att
define Aligned
define English Orthography .o. Aligned;
```

HFST import: `hfst-txt2fst -e '@0@' -i data/english-ipa-relation.att -o english.hfst`.
Interactive input tokenizers may recognize a chunk like `sh` as atomic; use
explicit character strings (`{sh}` in foma) when testing the upper side.

# Data provenance and redistribution

These data are derived from the Carnegie Mellon University Pronouncing
Dictionary (CMUdict): https://github.com/cmusphinx/cmudict . Retain the complete
copyright, redistribution conditions, and disclaimer in `CMUDICT-LICENSE.txt`
with both source data and generated artifacts. CMU permits modification and
redistribution under those conditions; the data should not be described as
public domain. The notice here was preserved from CMUdict 0.7b and matches the
current upstream notice.

The supplied alignment was transferred from the Linux server kay and is dated
March 16, 2023. It was produced using Phonetisaurus:
https://github.com/AdolfVonKleist/Phonetisaurus . Exact CMU revision and training
parameters have not yet been recovered. Document those when found. This is an
independent alignment/IPA derivative, not an official CMU release. Corrections
specific to alignment or IPA belong here; corrections to source pronunciations
can also be contributed upstream.

License for the new scripts remains for the repository owner to choose;
CMU's data notice does not automatically license our code. No Phonetisaurus
implementation or pretrained model is redistributed by this converter.

# Expanding phonetic chunks

The converter also writes `data/phonetic_chunk.att` by default. Override its
path with `--phonetic-output`, or suppress it with `--no-phonetic`. It maps each
atomic phonetic chunk to its sequence of individual atomic phones, preserving
stress, diphthongs, and affricates. For example, `j|u1` maps to `j u1`, while
`eɪ1` maps to the single symbol `eɪ1`. Explicit NULL maps to epsilon; this is
a pronunciation projection rather than an alignment-preserving display.
With an epsilon relation there is no explicit null mapping to add.

The build saves both `phonetic_chunk-cmu.att` and `phonetic_chunk-ipa.att`;
`phonetic_chunk.att` is a copy of the IPA map. Unlike orthographic chunking,
phonetic expansion is applied on the right. Take Kleene+ for whole sequences:

```
read att data/phonetic_chunk.att
define PhoneticChunk
define PhoneticExpansion PhoneticChunk+;
define EnglishPhones English .o. PhoneticExpansion;
```

As with orthographic maps, custom null or stress choices should have a matching
expansion map; save each configuration to its own path.
