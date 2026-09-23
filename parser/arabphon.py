"""
ArabPhon Rule-Based Phoneme Parser
Input : a fully diacritised Arabic word (with tashkil)
Output: IPA-style phoneme sequence as a list, e.g. ['k','a','t','a','b','a']

Handles:
  - Basic consonants + short vowels (fatha/kasra/damma)
  - Sukun (closed syllable, no vowel after consonant)
  - Shadda (gemination — consonant doubled)
  - Tanwin (fathatan/kasratan/dammatan → /an/, /in/, /un/)
  - Long vowels (medd): alef after fatha, ya after kasra, waw after damma
  - Sun-letter assimilation of ال (al-)
  - Hamza variants (all map to /ʔ/)
  - Ta marbuta (ة) → /a/ in pause form (grade 1 default)
  - Alef maqsura (ى) → /aː/
"""

# ── Unicode constants ──────────────────────────────────────────────────────────
FATHA     = 'َ'  # َ
KASRA     = 'ِ'  # ِ
DAMMA     = 'ُ'  # ُ
SUKUN     = 'ْ'  # ْ
SHADDA    = 'ّ'  # ّ
FATHATAN  = 'ً'  # ً
KASRATAN  = 'ٍ'  # ٍ
DAMMATAN  = 'ٌ'  # ٌ
TATWEEL   = 'ـ'  # ـ (kashida — ignore)

DIACRITICS = {FATHA, KASRA, DAMMA, SUKUN, SHADDA,
              FATHATAN, KASRATAN, DAMMATAN}

# ── Consonant map ──────────────────────────────────────────────────────────────
CONSONANTS = {
    'ب': 'b',  'ت': 't',  'ث': 'θ',  'ج': 'dʒ', 'ح': 'ħ',
    'خ': 'x',  'د': 'd',  'ذ': 'ð',  'ر': 'r',  'ز': 'z',
    'س': 's',  'ش': 'ʃ',  'ص': 'sˤ', 'ض': 'dˤ', 'ط': 'tˤ',
    'ظ': 'ðˤ', 'ع': 'ʕ',  'غ': 'ɣ',  'ف': 'f',  'ق': 'q',
    'ك': 'k',  'ل': 'l',  'م': 'm',  'ن': 'n',  'ه': 'h',
    'و': 'w',  'ي': 'j',
    # Hamza variants → glottal stop
    'ء': 'ʔ',  'أ': 'ʔ',  'إ': 'ʔ',  'آ': 'ʔ',  'ؤ': 'ʔ',  'ئ': 'ʔ',
    # Special
    'ة': 'h',   # ta marbuta — overridden in pause form below
    'ى': None,  # alef maqsura — handled as long vowel
    'ا': None,  # alef — handled as long vowel carrier
}

SUN_LETTERS = set('تثدذرزسشصضطظلن')

# ── Darija difficulty flags ────────────────────────────────────────────────────
DARIJA_ABSENT = {'θ', 'ð', 'ðˤ', 'sˤ', 'dˤ', 'q', 'ʔ'}


def parse_word(word: str, pause_form: bool = True) -> dict:
    """
    Parse a fully diacritised Arabic word into a phoneme sequence.

    Returns:
        {
          'word': original word,
          'phonemes': ['k','a','t','a','b','a'],
          'blending_script': 'k-a-t-a-b-a',
          'darija_flags': ['θ','ðˤ', ...],  # phonemes absent from Darija
          'difficulty': 'low' | 'medium' | 'high'
        }
    """
    # Remove kashida
    word = word.replace(TATWEEL, '')

    chars = list(word)
    phonemes = []
    i = 0

    # Handle definite article ال with sun-letter assimilation
    if len(chars) >= 2 and chars[0] == 'ا' and chars[1] == 'ل':
        # Find the next consonant after ال
        j = 2
        while j < len(chars) and chars[j] in DIACRITICS:
            j += 1
        if j < len(chars) and chars[j] in SUN_LETTERS:
            # Sun letter: ال → assimilate, e.g. الشَّمْس → aʃ-ʃams
            phonemes.append('a')
            # skip ا and ل, let the sun letter be doubled via shadda logic
            i = 2
        else:
            # Moon letter: ال → /al/
            phonemes.extend(['a', 'l'])
            i = 2

    while i < len(chars):
        ch = chars[i]

        # Skip standalone diacritics (already consumed with their consonant)
        if ch in DIACRITICS:
            i += 1
            continue

        # Look ahead for diacritics attached to this character
        diacritics_ahead = []
        j = i + 1
        while j < len(chars) and chars[j] in DIACRITICS:
            diacritics_ahead.append(chars[j])
            j += 1

        has_shadda   = SHADDA    in diacritics_ahead
        has_sukun    = SUKUN     in diacritics_ahead
        has_fatha    = FATHA     in diacritics_ahead
        has_kasra    = KASRA     in diacritics_ahead
        has_damma    = DAMMA     in diacritics_ahead
        has_fathatan = FATHATAN  in diacritics_ahead
        has_kasratan = KASRATAN  in diacritics_ahead
        has_dammatan = DAMMATAN  in diacritics_ahead

        # ── Alef madda (آ = ʔ + aː always) ──
        if ch == 'آ':
            phonemes.extend(['ʔ', 'aː'])
            i = j
            continue

        # ── Alef (long vowel carrier) ──
        # Only reached when alef was NOT already consumed by the fatha look-ahead above.
        # This happens for word-initial bare alef (undiacritised) — skip silently.
        if ch == 'ا':
            # Word-initial alef with kasra or damma = hamzat al-wasl → emit vowel
            if i == 0 or (len(phonemes) == 0):
                if has_kasra:
                    phonemes.append('i')
                elif has_damma:
                    phonemes.append('u')
                elif has_fatha:
                    phonemes.append('a')
            # else: mid-word bare alef = long vowel carrier (already handled by previous consonant's fatha→aː)
            i = j
            continue
        # ── Alef maqsura ──
        if ch == 'ى':
            phonemes.append('aː')
            i = j
            continue

        # ── Ta marbuta ──
        if ch == 'ة':
            if pause_form:
                # In pause form, ة is silent (the preceding vowel already covers it)
                pass
            else:
                phonemes.append('t')
                if has_fathatan:   phonemes.extend(['a', 'n'])
                elif has_kasratan: phonemes.extend(['i', 'n'])
                elif has_dammatan: phonemes.extend(['u', 'n'])
                elif has_fatha:    phonemes.append('a')
                elif has_kasra:    phonemes.append('i')
                elif has_damma:    phonemes.append('u')
            i = j
            continue  # <-- skips the vowel block below entirely

        # ── Regular consonant ──
        consonant_ipa = CONSONANTS.get(ch)
        if consonant_ipa is None:
            # Unknown character — skip
            i = j
            continue

        # Shadda = gemination (consonant said twice)
        if has_shadda:
            phonemes.append(consonant_ipa)
            phonemes.append(consonant_ipa)
        else:
            phonemes.append(consonant_ipa)

        # Implied vowels for hamza carriers with no explicit diacritic
        no_explicit_vowel = not (has_fatha or has_kasra or has_damma or has_sukun or
                                 has_fathatan or has_kasratan or has_dammatan)
        if no_explicit_vowel:
            if ch == 'أ':
                phonemes.append('a')
            elif ch in ('إ', 'ئ'):
                phonemes.append('i')
            elif ch == 'ؤ':
                phonemes.append('u')
            # ء, آ → no implied vowel (آ already handled above)

        # Vowel after consonant
        if has_fathatan:
            phonemes.extend(['a', 'n'])
            # Consume the orthographic alef that follows fathatan (spelling convention, not a vowel)
            if j < len(chars) and chars[j] == 'ا':
                j += 1
        elif has_kasratan:
            phonemes.extend(['i', 'n'])
        elif has_dammatan:
            phonemes.extend(['u', 'n'])
        elif has_fatha:
            # Check next non-diacritic char for long vowel (medd)
            # Only bare alef (ا) and alef maqsura (ى) extend to /aː/
            # Hamza-bearing alef variants are NOT medd — they are the next consonant
            next_char = chars[j] if j < len(chars) else ''
            if next_char == 'ا':
                phonemes.append('aː')
                j += 1  # consume the alef
            elif next_char == 'ى':
                phonemes.append('aː')
                j += 1
            else:
                phonemes.append('a')
        elif has_kasra:
            next_char = chars[j] if j < len(chars) else ''
            # Only treat ي as long-vowel extension if it carries NO diacritics of its own
            if next_char == 'ي':
                k = j + 1
                next_ya_diac = []
                while k < len(chars) and chars[k] in DIACRITICS:
                    next_ya_diac.append(chars[k])
                    k += 1
                if not next_ya_diac:
                    # bare ي = long /iː/
                    phonemes.append('iː')
                    j += 1
                else:
                    # ي has its own diacritics → short /i/, leave ي to be processed next
                    phonemes.append('i')
            else:
                phonemes.append('i')
        elif has_damma:
            next_char = chars[j] if j < len(chars) else ''
            if next_char == 'و':
                phonemes.append('uː')
                j += 1
                # Consume orthographic alef after waw (e.g. بَرَعُوا — the ا is silent)
                if j < len(chars) and chars[j] == 'ا':
                    j += 1
            else:
                phonemes.append('u')
        elif has_sukun:
            pass  # no vowel — closed syllable
        # else: no diacritic — undiacritised character, skip vowel

        i = j

    # ── Darija difficulty ──
    flags = [p for p in phonemes if p in DARIJA_ABSENT]
    n = len(flags)
    difficulty = 'low' if n == 0 else ('medium' if n <= 2 else 'high')

    return {
        'word': word,
        'phonemes': phonemes,
        'blending_script': '-'.join(phonemes),
        'darija_flags': flags,
        'difficulty': difficulty,
    }


# ── Batch processing ───────────────────────────────────────────────────────────
def parse_text(text: str) -> list:
    """Parse all words in a text string."""
    results = []
    for word in text.split():
        word = word.strip('،.,؟!()[]""')
        if word:
            results.append(parse_word(word))
    return results


# ── Demo ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    test_words = [
        'كَتَبَ',      # kataba
        'الشَّمْسُ',   # aʃ-ʃamsu (sun letter assimilation + shadda + sukun)
        'مَدْرَسَةٌ',  # madrasa (tanwin dammatan)
        'ثَعْلَبٌ',    # θaʕlabun (difficult: θ and ʕ absent from Darija)
        'بِسْمِ',      # bismi (sukun)
        'كِتَابٌ',     # kitaːbun (long vowel)
    ]

    print(f"{'Word':<20} {'Phonemes':<35} {'Difficulty':<10} {'Darija flags'}")
    print('-' * 80)
    for w in test_words:
        r = parse_word(w)
        print(f"{r['word']:<20} {r['blending_script']:<35} {r['difficulty']:<10} {r['darija_flags']}")
