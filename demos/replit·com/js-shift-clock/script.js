// Open a Console Stdout

const tt0 = document.createElement("p")
tt0.style.fontFamily = '"Courier New", Courier, mono'
document.body.appendChild(tt0)

tt0.innerText = ""

function print(text) {
    //tt0.innerText += text.toString() + "\n"
    //tt0.innerHTML += text.toString() + "$<br>"
    tt0.innerHTML += text.toString() + "<br>"
}


// Halt at trouble

function assert(truthy, occasion) {
    if (!truthy) {
        throw occasion || "AssertionError"
    }
}


// Capture some clock-in/ clock-out hour.minute time Stamps
// but what does ``` mean?

text_a = ""; text_a += `

    7.21..8.36
    9.03..9.34
    9.50..10.28
    11.04..16.24
    16.49..17.19

`; text_a += ""

text_b = ""; text_b += `

    8.00..9.00
    10.15..11.24
    15.18..21.54
    
`; text_b += ""

text = text_a


// Visit each Pair of Stamps

matches = text.match(/[0-9]+[.][0-9]+/g)

summed_total = 0

assert((matches.length % 2) == 0, matches.length)
for (var i = 0; i < matches.length; ++i) {
    chars = matches[i]
    splits = chars.split(".")
    str_h = splits[0]
    str_m = splits[2 - 1]

    if ((i % 2) == 0) {
        str_h0 = str_h
        str_m0 = str_m
    } else {
        dh = Number(str_h) - Number(str_h0)
        dm = Number(str_m) - Number(str_m0)

        total = (dh * 60) + dm
        minutes = total % 60
        hours = (total - minutes) / 60

        summed_total += total

        print(`${str_h0}:${str_m0} ${str_h}:${str_m} -> ${hours}h${minutes}m`)
    }
}

summed_minutes = summed_total % 60
summed_hours = (summed_total - summed_minutes) / 60

print("")
print(`${summed_hours}h${summed_minutes}m total`)