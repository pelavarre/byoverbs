// Open a Console Stdout

p_chosen = p_sh_date

function print(text) {
    //p_chosen.innerText += text.toString() + "\n"
    //p_chosen.innerHTML += text.toString() + "$<br>"
    p_chosen.innerHTML += text.toString() + "<br>"
}


// Halt at trouble

function assert(truthy, occasion) {
    if (!truthy) {
        throw occasion || "AssertionError"
    }
}


// Say how to center text inside a Line of Spaces

function dent_to_center(text, width) {
    if (width < text.length) {
        return text
    }

    _00A0_Nbsp = "\u00A0"
    dent = _00A0_Nbsp.repeat(Math.floor((width - text.length) / 2))
    dented = dent + text

    return dented
}

// Look a fortnight ahead and behind

now = new Date()

year = now.getFullYear()
month = 1 + now.getMonth()
day = now.getDate()

mm = ("00" + month.toString()).slice(-2)
dd = ("00" + day.toString()).slice(-2)
yyyy_mm_dd = `${year}-${mm}-${dd}`

hh = ("00" + now.getHours().toString()).slice(-2)
mm_ = ("00" + now.getMinutes().toString()).slice(-2)
ss = ("00" + now.getSeconds().toString()).slice(-2)
hh_mm_ss = `${hh}:${mm_}:${ss}`

west = now.getTimezoneOffset()
sign = (west > 0) ? "-" : "+"  // -West or +East of UTC, we say
mag = Math.abs(west)

assert(mag <= 99 * 60, west)  // often: mag <= 24 * 60 == 1440
mag_h = Math.trunc(mag / 60)
mag_m = mag % 60
mag_hh = ("00" + mag_h.toString()).slice(-2)
mag_mm = ("00" + mag_m.toString()).slice(-2)

zone = `-${mag_hh}:${mag_mm}`  // '-08:00'

// Print now, a la Sh Date

p_chosen = p_sh_date
p_chosen.style.fontFamily = '"Courier New", Courier, mono'

print("+ date -Iseconds")
print(`${yyyy_mm_dd}T${hh_mm_ss}${zone} `)
print("+")


// Print one or two Calendar Months, a la Sh Cal & NCal

p_chosen = p_sh_cal
p_chosen.style.fontFamily = '"Courier New", Courier, mono'

before = new Date(now)
before.setDate(now.getDate() - 14);

after = new Date(now)
after.setDate(now.getDate() + 14);

focus_year = before.getFullYear()
focus_month = before.getMonth() + 1

for (let tried = 0; tried < 2; tried++) {
    if (tried) {
        print("")
    }

    focus = new Date(focus_year, focus_month - 1, 1)

    if (focus_month == month) {
        mac_shline = `cal -H ${yyyy_mm_dd} -m ${month} ${year} `
        linux_shline = `ncal -b -H ${yyyy_mm_dd} -m ${month} ${year} `
    } else {
        mac_shline = `cal -h -m ${focus_month} ${focus_year} `
        linux_shline = `ncal -b -h -m ${focus_month} ${focus_year} `
    }

    print(`+ ${mac_shline} `)
    print(`+ ${linux_shline} `)
    print("")

    month_longname = focus.toLocaleString("default", { month: "long" })
    title = `${month_longname} ${focus_year} `
    print(dent_to_center(title, "Su Mo Tu We Th Fr Sa".length))

    print("Su Mo Tu We Th Fr Sa")

    _0_Sunday = 0
    while (focus.getDay() != _0_Sunday) {
        focus.setDate(focus.getDate() - 1)
    }

    _00A0_Nbsp = "\u00A0"
    for (let i = 0; i < 6; ++i) {
        line = ""
        for (let j = 0; j < 7; ++j) {
            if (j) { line += " " }
            if (focus.getMonth() < (focus_month - 1)) {
                line += _00A0_Nbsp + _00A0_Nbsp
            } else if (focus.getMonth() > (focus_month - 1)) {
                break
            } else {
                fdd = (_00A0_Nbsp + focus.getDate().toString()).slice(-2)
                if ((focus_month == month) && (focus.getDate() == day)) {
                    // line += "**"
                    line += `<strong> ${fdd}</strong> `
                } else {
                    line += `${fdd} `
                }
            }
            focus.setDate(focus.getDate() + 1)
        }
        if (line) {
            print(line)
        }
    }

    if (before.getMonth() == after.getMonth()) {
        break
    }

    focus_year = after.getFullYear()
    focus_month = after.getMonth() + 1
}

print("")
print("+")

//

const ttn = document.createElement("p")
document.body.appendChild(ttn)
ttn.innerText = "Ta da"