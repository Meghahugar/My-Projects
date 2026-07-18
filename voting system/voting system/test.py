import sqlite3
place = 'bengaluru-urban'
connection = sqlite3.connect(f"{place}.db")
cursor = connection.cursor()
cursor.execute("create table if not exists voting (voter TEXT, candidate_name TEXT, party_name TEXT, election_symbol TEXT, image TEXT)")

cursor.execute("select * from voting")
result = cursor.fetchall()
if result:
    result = list(set(result))

    conn = sqlite3.connect("database.db")
    cr = conn.cursor()
    cr.execute("select * from candidates where place = '"+place+"'")
    List = cr.fetchall()
    candidates = []
    parties = []
    for row in List:
        candidates.append(row[1])
        parties.append(row[3])

    votes = []
    
    for name in candidates:
        cursor.execute("select * from voting where candidate_name = '"+name+"'")
        res = cursor.fetchall()
        if res:
            votes.append(int(len(res)/2))
        else:
            votes.append(0)
    
    rows = []
    for i in range(len(parties)):
        rows.append([parties[i], candidates[i], votes[i]])
    print(rows)