#!/bin/sh
# Run from any directory. PYTHON may select a particular interpreter.
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
python=${PYTHON:-python3}
for phones in cmu ipa; do
    for representation in relation interleaved pairs; do
        "$python" "$root/script/aligned_to_att.py" --phones "$phones" \
            --representation "$representation" \
            --phonetic-output "$root/data/phonetic_chunk-$phones.att" \
            --output "$root/data/english-$phones-$representation.att"
    done
    "$python" "$root/script/aligned_to_att.py" --phones "$phones" --epsilon \
        --no-orthographic --no-phonetic --output "$root/data/english-$phones-epsilon.att"
done

# Default phonetic expansion uses IPA with stress, matching the default converter.
cp "$root/data/phonetic_chunk-ipa.att" "$root/data/phonetic_chunk.att"
