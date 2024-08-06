# reads in from file og_history.txt
# puts result into file new_history.txt
# format: each bill starts with !HOUSE NUMBER, empty line, history, empty line x2, new bill + history
# history is read from capitol track bill history


def main(): 
    house = "ERROR"
    number = "ERROR"
    committee = "ERROR"
    output = open('./new_history.txt', 'w')
    history = []

    og_history = open("og_history.txt", "r")
    lines = og_history.readlines()
    line_amount = len(lines)
    lines = reversed(lines)

    print("---------------", file=output)

    for index, line in enumerate(lines):
        if line[0] == "!":
            house = line[1]
            number = line[4:]
            if history:
                print_history(history, output)
            history = []
            history.append("Bill " + house + "B " + number)
        if "(Ayes " in line:
            date = get_date(line)
            count = get_vote_count(line)
            if "Read third time" in line:
                history.append(date + " Passed by " + house_expansion(house) + " " + count)
                house = flip_house(house)
            elif "amendments concurred in" in line:
                history.append(date + " Passed by " + house_expansion(house) + " " + count)
                house = flip_house(house)
            elif "be concurred in" in line:
                1+1
            else:
                history.append(date + " Passed by " + house + ". " + expand_committee(committee, history) + " Committee " + count)
        if ("re-referred" in line.lower()) or ("referred" in line.lower()):
            committee = get_committee(line, committee)
        if "Approved by the Governor" in line:
            date = get_date(line)
            history.append(date + " Signed into law by Governor")
        if index == line_amount -1:
            print_history(history, output)

def print_history(history, output):
    bill_line = "ERROR"
    if bill_line:
        bill_line = history[0]
    history.extend([bill_line, ""])
    history = history[1:]
    reversed_history = '\n'.join(reversed(history))
    print(reversed_history + "\n" + "\n" + "---------------", file=output)

def get_date(line):
    month_end = line.find(" ")
    month = get_month(line[:month_end])
    line = line[month_end+1:]

    day_end = line.find(",")
    day = line[:day_end]
    if day[0] == "0":
        day = day[1:]
    line = line[day_end+2:]

    year = line[:4]

    return month + "/" + day + "/" + year

def get_month(month):
    month = month.lower()
    if month == "jan":
        return "1"
    elif month == "feb":
        return "2"
    elif month == "mar":
        return "3"
    elif month == "apr":
        return "4"
    elif month == "may":
        return "5"
    elif month == "jun":
        return "6"
    elif month == "jul":
        return "7"
    elif month == "aug":
        return "8"
    elif month == "sep":
        return "9"
    elif month == "oct":
        return "10"
    elif month == "nov":
        return "11'"
    elif month == "dec":
        return "12'"
    else:
        return "ERROR"

def get_vote_count(line):
    vote_start = line.find("(Ayes")
    line = line[vote_start + 6:]

    aye_end = line.find(".")
    aye_vote = line[:aye_end]

    no_end = line.find(".)")

    no_vote = line[aye_end+7 : no_end]

    return "(" + aye_vote + "-" + no_vote + ")"

def house_expansion(house):
    if house == "A":
        return "Assembly"
    if house == "S":
        return "Senate"
    print("House error")
    return "ERROR"

def flip_house(curr_house):
    if curr_house == "A":
        return "S"
    if curr_house == "S":
        return "A"
    return "ERROR"

def get_committee(line, curr_committee):
    if "suspense file" in line:
        return curr_committee

    line = line.lower()
    keyword = "re-referred" if ("re-referred" in line) else "referred"
    start = line.find(keyword) + len(keyword) + 12
    # for "keyword to Com. on "
    line = line[start:]
    committee = line[:line.find("(")]
    if "pursuant" in committee:
        committee = committee[:committee.find(" pursuant")]
    return committee

def expand_committee(committee, history):
    # ordered alphabetically according to the expanded name
    if committee == "aging & l.t.c.":
        return "Aging and Long-Term Care"
    elif committee == "appr." or committee == "appr. ":
        return "Appropriations"
    elif committee == "ed.":
        return "Education"
    elif committee == "elections.":
        return "Elections"
    elif committee == "e. & c.a.":
        return "Elections and Constitutional Amendments"
    elif committee == "e.s. & t.m.":
        return "Environmental Safety and Toxic Materials"
    elif committee == "e.q":
        return "Environmental Quality"
    elif committee == "g.o.":
        return "Governmental Organizations"
    elif committee == "health.":
        return "Health"
    elif committee == "higher ed.":
        return "Higher Education"
    elif committee == "hum. s.":
        return "Human Services"
    elif committee == "ins.":
        return "Insurance"
    elif committee == "jud.":
        return "Judiciary"
    elif committee == "l., p.e. & r.":
        return "Labor, Public Employees, and Retirement"
    elif committee == "m. & v.a.":
        return "Military and Veterans Affairs"
    elif committee == "p. & c.p.":
        return "Privacy and Consumer Protection"
    elif committee == "p.e. & r.":
        return "Public Employment and Retirement"
    elif committee == "pub. s." or committee == "pub s.":
        return "Public Safety"
    elif committee == "rev. & tax.":
        return "Revenue and Tax"
    
    print("Oops, this script does not have an expansion for " + committee + " committee on " + history[0][:-1])
    print("Either you need to update the committee expansions or manually fix the spot in " + history[0][:-1] + "'s history that says 'ERROR'\n")
    return "ERROR"

if __name__=="__main__":
    main()