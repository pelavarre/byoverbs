_ = """

(set -x; set |grep ^.=; set |grep ^..=)  # shows a mostly empty namespace
diff -brpu <(export) <(set) |sort |grep -v '[ +]'  # shows Export's listed as Set's

bind 'set enable-bracketed-paste off' 2>/dev/null; unset zle_bracketed_paste

echo a
echo b
echo c
"""
