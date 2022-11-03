pid=$(
    (screen -ls || :) |grep '\t'| head -$1 |tail -1 |
        tr -d '\t' |cut -d. -f1
)
(set -xe && screen -r $pid)
