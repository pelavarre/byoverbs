# echo a b c d e f |tr ' ' '\n' |awk '(NR<=2){print NR":",$0} {o2=o1} {o1=$0} END{print (NR-1)":", o2; print NR":", o1}'
# echo a b c d e f |tr ' ' '\n' |cat -n |expand |tee >(head -2) >(tail -2) >/dev/null  # more cogent, less reliable


# posted as:  https://github.com/pelavarre/byoverbs/blob/main/bin/tail.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
