set -e

last=$#
py=p.py
if [[ $last != 0 ]]; then
    py=${!last}
fi

index=1
while [[ $index -le $last ]]; do
    arg=${!index}
    if [[ $arg =~ [.]py$ ]]; then
        py=$arg

        break

    fi
    index=$((index + 1))
done

echo +
echo "+ echo |python3 -m pdb $py" >&2
echo |python3 -m pdb $py

echo +
echo "+ black $py" >&2
black $py

echo +
echo "+ flake8 $py" >&2
flake8 $py

echo +

echo +
echo '+ python3' "$@" >&2
python3 "$@"
