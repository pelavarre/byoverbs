# find .  # isn't implied by 'find' without Sh Args at Mac
# find / -mount 2>/dev/null |grep ...

# find -size +1001k 2>/dev/null
# ls -hlAF -rt -rS $(find . -size +1001k 2>/dev/null)

# find . -maxdepth 1 -not -perm -111 -not -type d
# find . -maxdepth 1 -perm -111 -not -type d
# find . -not -type d -not -path './.git/*'
# git ls-files

# cd bin/ && find bin/find.py should work sometimes

# touch -d 2024-01-01T00:00:00 2023/2024-01-01
# touch -d 2024-01-01 2023/2024-01-01  # Linux accepts T00:00:00 abbreviated
# find . -not -newer 2023/2024-01-01  # finds the first Second of the New Year too :-(


# posted into:  https://github.com/pelavarre/byoverbs/blob/main/bin/find.py
# copied from:  git clone https://github.com/pelavarre/byoverbs.git
