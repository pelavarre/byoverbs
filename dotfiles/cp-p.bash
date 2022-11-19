cd dotfiles/
for F in dot.*; do
    if [[ "$F" != "dot.gitconfig" ]]; then  # 'user.initials' etc not anonymized :-(
        cp -p ~/$(echo $F |sed 's,^dot,,') $F
    fi
done
