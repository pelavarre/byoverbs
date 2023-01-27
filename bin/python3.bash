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

set -xe

echo |python3 -m pdb $py
black $py
flake8 $py
:
:
python3 "$@"
