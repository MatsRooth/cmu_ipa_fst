# CMU phones and IPA: spelling examples

This table uses the project's broad American English phone conventions.
Bold letters illustrate spellings associated with the target phone; they are
teaching cues, not claims about the aligner's exact chunk boundaries.

| CMU | IPA | Orthographic examples |
|---|---|---|
| AA | ɑ | f**a**ther, h**o**t, p**al**m |
| AE | æ | c**a**t, bl**a**ck, l**au**gh |
| AH1 / AH2 | ʌ | c**u**p, l**o**ve, bl**oo**d |
| AH0 | ə | **a**bout, sof**a**, probl**e**m |
| AO | ɔ | l**aw**, th**ough**t, c**au**ght |
| AW | aʊ | c**ow**, **ou**t, h**ou**se (noun) |
| AY | aɪ | t**i**me, n**igh**t, m**y** |
| B | b | **b**at, ra**bb**it |
| CH | tʃ | **ch**air, wa**tch**, **c**ello |
| D | d | **d**og, la**dd**er, play**ed** |
| DH | ð | **th**is, mo**th**er, brea**th**e |
| EH | ɛ | b**e**d, h**ea**d, s**ai**d |
| ER | ɹ̩ | b**ir**d, l**ear**n, n**ur**se |
| EY | eɪ | r**a**te, b**ai**t, d**ay** |
| F | f | **f**an, **ph**one, lau**gh** |
| G | ɡ | **g**o, e**gg**, **gh**ost |
| HH | h | **h**at, **h**ouse |
| IH | ɪ | s**i**t, g**y**m, b**u**sy |
| IY | i | s**ee**, k**ey**, mach**i**ne |
| JH | dʒ | **j**am, **g**iant, bri**dge** |
| K | k | **c**at, **k**ite, ba**ck** |
| L | l | **l**ip, be**ll** |
| M | m | **m**an, su**mm**er, la**mb** |
| N | n | **n**et, ru**nn**er, **kn**ee |
| NG | ŋ | si**ng**, thi**n**k |
| OW | oʊ | n**o**, b**oa**t, sn**ow** |
| OY | ɔɪ | b**oy**, c**oi**n |
| P | p | **p**en, ha**pp**y |
| R | ɹ | **r**ed, ca**rr**y, **wr**ite |
| S | s | **s**un, **c**ity, mi**ss** |
| SH | ʃ | **sh**ip, na**ti**on, ma**ch**ine |
| T | t | **t**op, ca**t**, miss**ed** |
| TH | θ | **th**in, ba**th** |
| UH | ʊ | p**u**t, g**oo**d, c**ou**ld |
| UW | u | bl**ue**, f**oo**d, sh**oe** |
| V | v | **v**an, lea**v**e |
| W | w | **w**et, **w**e |
| Y | j | **y**es, **y**ard |
| Z | z | **z**oo, ro**s**e, bu**zz** |
| ZH | ʒ | vi**si**on, mea**s**ure, bei**g**e |

All 39 base mappings match the reference table at
https://github.com/matthewmorrone/cmudict-ipa/blob/master/data/mappings/ipa.tsv .
The additional schwa row reflects our AH0 -> ə conversion. Vowel stress
suffixes are omitted here: in the FST, 0 means unstressed, 1 primary stress,
and 2 secondary stress, e.g. eɪ1. A | inside an FST chunk separates phones;
it is not an IPA sound.

Pronunciation varies by dialect. In particular, many American speakers merge
ɑ and ɔ (cot/caught). ER is written as syllabic ɹ̩ in this project; ɝ is another
common notation for the stressed rhotic vowel. No vowel length marks are used.
The T row denotes the broad phoneme, which may have different surface
realizations. These examples do not imply that a spelling always has this sound.
