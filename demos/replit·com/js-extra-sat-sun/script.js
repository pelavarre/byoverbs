// Open a Console Stdout

extra_div_element = document.createElement("div")
main_div = extra_div_element

function print(textish) {

    const div_element = document.createElement("div")
    div_element.style.fontFamily = '"Courier New", Courier, mono'
    document.body.appendChild(div_element)

    hmarkup = textish.toString()
    div_element.innerHTML = hmarkup

    if (hmarkup.match("2028")) {
        main_div = div_element
    }
}


// Halt at trouble

function assert(truthy, occasion) {
    if (!truthy) {
        throw occasion || "AssertionError"
    }
}


// Across a range of years,
// add up Mo Tu We Th Fr, and Sa Su

for (let y = 2058; y >= 1939; --y) {
    d0 = new Date(y, 1 - 1, 1)
    wd0 = d0.getDay()

    // Count up how many of each Day-of-Week Su .. Sa

    counts = [0, 0, 0, 0, 0, 0, 0]
    d = d0
    while (d.getFullYear() == y) {
        counts[d.getDay()] += 1
        d.setDate(d.getDate() + 1)
    }

    // Style the Count as Strong when it's large

    cc = counts.slice()
    for (let wd = 0; wd < 7; wd++) {
        if (counts[wd] > 52) {
            cc[wd] = `<strong>${counts[wd]}</strong>`
        }
    }

    // Across the year, sum up Weekdays/ Weekends

    dd = counts
    costs = dd[1] + dd[2] + dd[3] + dd[4] + dd[5]
    profits = dd[0] + dd[6]

    // Style a mention of the first Day-of-Week of Year

    day_code = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
    assert(wd0 < day_code.length, wd0)
    swd0 = day_code[wd0]
    if (wd0 == 6) {
        swd0 = `<strong>${swd0}</strong>`
    }

    // Form the Html Markup of a Table Row

    s = `| ${y} | ${swd0}`
    if (profits >= 106) {
        s += (` | <strong>${costs}</strong> | <strong>${profits}</strong> |`)
    } else {
        s += (` | ${costs} | ${profits} |`)
    }

    // Print the Markup

    print(s)
}

my_main_rect = main_div.getBoundingClientRect()
//console.log(`rect=${JSON.stringify(rect)}`)  // {"x":8,"y":636.79...
console.log('my_main_rect =', my_main_rect)

doc_rect = document.body.getBoundingClientRect()
console.log('doc_rect =', doc_rect)

//window.scrollTo(0, doc_rect.height / 2)
window.scrollTo(0, my_main_rect.y / 2)
