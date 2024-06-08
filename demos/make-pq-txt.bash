#!/bin/bash

set -x

function func() {
    (set -xe; bin/pq.py --py "$@") || echo + exit $?
}

echo +

func bytes len
func text len
func lines len
func words len

func set

func close
func dedent
func dent
func frame
func end
func lstrip
func reverse
func rstrip
func shuffle
func sort
func strip
func undent

func closed
func dedented
func dented
func ended
func framed
func lstripped
func rstripped
func reversed
func sorted
func shuffled
func stripped
func undented

echo '{"//":[""]}' |func jq
func tac
func tail r
func uniq
func wc c
func wc l
func wc m
func wc w
func xargs

func s
func u
func x
func xn1

echo +
