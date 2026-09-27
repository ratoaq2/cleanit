# Check a rule change against real subtitles

Rule examples and fixture cases cannot show if a pattern damages real dialogue. For a broad rule change,
run the rules on a local corpus of real subtitles before the merge.

## The corpus

The corpus is local. It is not in git, because real subtitles are copyrighted content. The `target/`
folder is gitignored. The maintainer keeps the files in `target/input/` (movies and series, several
thousand `.srt` files in English, Brazilian Portuguese, and German).

## Procedure

1. Do not read the corpus files into the AI context. They are too large.
2. Make a baseline: run the rules of `main` on a copy of the corpus. Use the same tags as your test, for
   example `-t default`.
3. Run the rules of your branch on another copy.
4. Record each change of each rule. Patch `cleanit.rule.Rule.apply` in a script, and write the rule name,
   the text before, and the text after to a file.
5. Group the changes by rule and by a short diff signature (`difflib`). Read the distinct signatures of
   each rule. Rules with few matches often hide the damage.
6. Also check the full corpus:
   - The timestamps do not change.
   - No entry is added.
   - The count of each character changes only in the expected way.

A full run takes 20 to 30 minutes. Run it in the background, and write all output to a file.
