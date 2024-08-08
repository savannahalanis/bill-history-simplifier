# reads in from file og_history.txt
# puts result into file new_history.txt
# format: each bill starts with !HOUSE NUMBER\n, empty line, history, empty line x2, new bill + history
# history is read from capitol track bill history

# possible TODO - add if bill died, rip bill

import re


def main(): 
    house = "ERROR"
    number = "ERROR"
    committee = "ERROR"
    output = open('./new_history.txt', 'w')
    history = []
    multiple_committees = []

    og_history = open("og_history.txt", "r")
    lines = og_history.readlines()
    line_amount = len(lines)
    lines = reversed(lines)

    print("---------------", file=output)

    for index, line in enumerate(lines):
        status = "Passed by"
        if "Failed" in line or "failed" in line:
            status = "Failed in"
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
            if multiple_committees:
                replacement = find_one_not_in_list(line, multiple_committees)
                if replacement != "ERROR":
                    committee = replacement
                else:
                    print("Oops, it is ambiguous to determine a committee in " + history[0][:-1] + ". Please manually put in the committee in the spot that says 'COMMITTEE_TBD'. It has a date of " + date +" and vote count of " + count + "." + "\n")
            if "Read third time" in line:
                history.append(date + " " + status + " " + house_expansion(house) + " " + count)
                house = flip_house(house)
            elif "amendments concurred in" in line:
                history.append(date + " " + status + " " + house_expansion(house) + " " + count)
                house = flip_house(house)
            elif "be concurred in" in line:
                1+1
            else:
                history.append(date + " " + status + " " + house + ". " + expand_committee(committee, history) + " Committee " + count)
        if ("re-referred" in line.lower()) or ("referred" in line.lower()):
            committee, multiple_committees = get_committee(line, committee)
        if "Approved by the Governor" in line:
            date = get_date(line)
            history.append(date + " Signed into law by Governor")
        if index == line_amount -1:
            print_history(history, output)

def find_one_not_in_list(str, lst):
    str = str.lower()
    str = str[str.index("refer"):]
    num = len(lst)

    # to handle that "ed." is in "higher ed."
    if "higher ed." in lst:
        str = str.replace("higher ed.", "higher ED.")
    str = re.sub(r'[a-z]+ed', "", str)

    for item in lst:
        if item == "higher ed.":
            item = "higher ED."
        if item in str:
            num = num - 1

    if num == 1:
        for item in lst:
            if not (item in str):
                return item
    
    return "ERROR"

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

    no_end = find_nth_index(line, ".", 2)

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
        return curr_committee, []
    
    # get committee(s)
    line = line.lower()
    keyword = "re-referred" if ("re-referred" in line) else "referred"
    start = line.find(keyword) + len(keyword) + 12 # for "keyword to Com. on "
    line = line[start:]
    committee = line[:line.find("(")]
    if "pursuant" in committee:
        committee = committee[:committee.find(" pursuant")]

    # if multiple committees, put into multiple_committees list
    if ("," in committee) or ("and" in committee):

        if committee == "l., p.e. & r.": # this is one committee, not multiple
            return committee, []

        committee = committee[1:] # chop off the first char bc "keyword to Coms. on " means extra character

        mult_committees = []
        start = 0
        end = 0
        comma_count = committee.count(",")

        for i in range(comma_count):
            end = find_nth_index(committee, ",", i+1)
            item = committee[start:end]
            if expand_committee(item, []) != "ERROR":
                mult_committees.append(item)
                start = end + 2

        if "and" in committee:
            and_index = committee.index("and")
            item1 = committee[start:and_index-1]
            item2 = committee[and_index+4:]

            if expand_committee(item1, []) != "ERROR":
                mult_committees.append(item1)

            if expand_committee(item2, []) != "ERROR":
                mult_committees.append(item2)
        
        return "COMMITTEE_TBD", mult_committees

    # if one committee
    return committee, []

def find_nth_index(str, target, n):
    count = 0
    for index, c in enumerate(str):
        if c == target:
            count += 1
            if count == n:
                return index
    return -1

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
    elif committee == "e.q.":
        return "Environmental Quality"
    elif committee == "g.o.":
        return "Governmental Organizations"
    elif committee == "health.":
        return "Health"
    elif committee == "higher ed.":
        return "Higher Education"
    elif committee == "hum. s." or committee == "human s.":
        return "Human Services"
    elif committee == "ins.":
        return "Insurance"
    elif committee == "jud.":
        return "Judiciary"
    elif committee == "l. & e.":
        return "Labor and Employment"
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
    
    elif committee == "COMMITTEE_TBD":
        return committee
    
    if history:
        print("Oops, this script does not have an expansion for " + committee + " committee on " + history[0][:-1])
        print("Either you need to update the committee expansions or manually fix the spot in " + history[0][:-1] + "'s history that says 'ERROR'\n")

    return "ERROR"

if __name__=="__main__":
    main()

