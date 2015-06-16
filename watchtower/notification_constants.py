# from https://neweden-dev.com/Char/Notifications
_table = """
1   Legacy
2   Character deleted
3   Give medal to character
4   Alliance maintenance bill
5   Alliance war declared
6   Alliance war surrender
7   Alliance war retracted
8   Alliance war invalidated by Concord
9   Bill issued to a character
10  Bill issued to corporation or alliance
11  Bill not paid because there's not enough ISK available
12  Bill, issued by a character, paid
13  Bill, issued by a corporation or alliance, paid
14  Bounty claimed
15  Clone activated
16  New corp member application
17  Corp application rejected
18  Corp application accepted
19  Corp tax rate changed
20  Corp news report, typically for shareholders
21  Player leaves corp
22  Corp news, new CEO
23  Corp dividend/liquidation, sent to shareholders
24  Corp dividend payout, sent to shareholders
25  Corp vote created
26  Corp CEO votes revoked during voting
27  Corp declares war
28  Corp war has started
29  Corp surrenders war
30  Corp retracts war
31  Corp war invalidated by Concord
32  Container password retrieval
33  Contraband or low standings cause an attack or items being confiscated
34  First ship insurance
35  Ship destroyed, insurance payed
36  Insurance contract invalidated/runs out
37  Sovereignty claim fails (alliance)
38  Sovereignty claim fails (corporation)
39  Sovereignty bill late (alliance)
40  Sovereignty bill late (corporation)
41  Sovereignty claim lost (alliance)
42  Sovereignty claim lost (corporation)
43  Sovereignty claim acquired (alliance)
44  Sovereignty claim acquired (corporation)
45  Alliance anchoring alert
46  Alliance structure turns vulnerable
47  Alliance structure turns invulnerable
48  Sovereignty disruptor anchored
49  Structure won/lost
50  Corp office lease expiration notice
51  Clone contract revoked by station manager
52  Corp member clones moved between stations
53  Clone contract revoked by station manager
54  Insurance contract expired
55  Insurance contract issued
56  Jump clone destroyed
57  Jump clone destroyed
58  Corporation joining factional warfare
59  Corporation leaving factional warfare
60  Corporation kicked from factional warfare on startup because of too low standing to the faction
61  Character kicked from factional warfare on startup because of too low standing to the faction
62  Corporation in factional warfare warned on startup because of too low standing to the faction
63  Character in factional warfare warned on startup because of too low standing to the faction
64  Character loses factional warfare rank
65  Character gains factional warfare rank
66  Agent has moved
67  Mass transaction reversal message
68  Reimbursement message
69  Agent locates a character
70  Research mission becomes available from an agent
71  Agent mission offer expires
72  Agent mission times out
73  Agent offers a storyline mission
74  Tutorial message sent on character creation
75  Tower alert
76  Tower resource alert
77  Station service aggression message
78  Station state change message
79  Station conquered message
80  Station aggression message
81  Corporation requests joining factional warfare
82  Corporation requests leaving factional warfare
83  Corporation withdrawing a request to join factional warfare
84  Corporation withdrawing a request to leave factional warfare
85  Corporation liquidation
86  Territorial Claim Unit under attack
87  Sovereignty Blockade Unit under attack
88  Infrastructure Hub under attack
89  Contact add notification
90  Contact edit notification
91  Incursion Completed
92  Corp Kicked
93  Customs office has been attacked
94  Customs office has entered reinforced
95  Customs office has been transferred
96  FW Alliance Warning
97  FW Alliance Kick
98  AllWarCorpJoined Msg
99  Ally Joined Defender
100     Ally Has Joined a War Aggressor
101     Ally Joined War Ally
102     New war system: entity is offering assistance in a war.
103     War Surrender Offer
104     War Surrender Declined
105     FacWar LP Payout Kill
106     FacWar LP Payout Event
107     FacWar LP Disqualified Eventd
108     FacWar LP Disqualified Kill
109     Alliance Contract Cancelled
110     War Ally Declined Offer
111     Your Bounty Claimed
112     Bounty Placed (Char)
113     Bounty Placed (Corp)
114     Bounty Placed (Alliance)
115     Kill Right Available
116     Kill Right Available Open
117     Kill Right Earned
118     Kill Right Used
119     Kill Right Unavailable
120     Kill Right Unavailable Open
121     Declare War
122     Offered Surrender
123     Accepted Surrender
124     Made War Mutual
125     Retracts War
126     Offered To Ally
127     Accepted Ally
128     Character Application Accept Message
129     Character Application Reject Message
130     Character Application Withdraw Message
137     Team Auction lost
138     Clone Activated(?)
140     Lossmail Available(?)
141     Killmail Available(?)
"""
_table_rows = _table.strip().split('\n')
_table_rows = [row.split(None, 1) for row in _table_rows]
notif_name = {int(id): name for id, name in _table_rows}
notif_id = {name: int(id) for id, name in _table_rows}

relevant_notif_types = {
    # wardecs?
    #11,  # bill not paid
    37,  # Sovereignty claim fails (alliance)
    38,  # Sovereignty claim fails (corporation)
    #39,  # Sovereignty bill late (alliance)
    #40,  # Sovereignty bill late (corporation)
    41,  # Sovereignty claim lost (alliance)
    42,  # Sovereignty claim lost (corporation)
    43,  # Sovereignty claim acquired (alliance)
    44,  # Sovereignty claim acquired (corporation)
    45,  # Alliance anchoring alert
    46,  # Alliance structure turns vulnerable
    47,  # Alliance structure turns invulnerable
    48,  # Sovereignty disruptor anchored
    49,  # Structure won/lost
    #69,  # Agent locates a character
    75,  # Tower alert
    77,  # Station service aggression message
    78,  # Station state change message
    79,  # Station conquered message
    80,  # Station aggression message
    86,  # Territorial Claim Unit under attack
    87,  # Sovereignty Blockade Unit under attack
    88,  # Infrastructure Hub under attack
    93,  # Customs office has been attacked
    94,  # Customs office has entered reinforced
}

notif_messages = {
    37: "XXX Sovereignty claimed failed {solarSystemID}",
    38: "XXX Sovereignty claimed failed {solarSystemID}",
    #39:  # Sovereignty bill late (alliance)
    #40:  # Sovereignty bill late (corporation)
    41: "XXX Sovereignty claim lost (alliance) {solarSystemID}",
    42: "XXX Sovereignty claim lost (corporation) {solarSystemID}",
    43: "XXX Sovereignty claim acquired (alliance) {solarSystemID}",
    44: "XXX Sovereignty claim acquired (corporation) {solarSystemID}",
    45: "Tower anchored {moonID} by {corpID}[{allianceID}]",
    46: "XXX Alliance structure turns vulnerable {solarSystemID}",
    47: "XXX Alliance structure turns invulnerable {solarSystemID}",
    48: "SBU anchored in {solarSystemID} by {corpID}[{allianceID}]",
    49: "XXX Structure won/lost {solarSystemID}",
    #69,  # Agent locates a character
    75: "Tower attacked {moonID} ({shieldValue}/{armorValue}/{hullValue}) by {aggressorCorpID}[{aggressorAllianceID}]",
    77: "Station service attacked {solarSystemID} ({shieldValue}/{armorValue}/{hullValue}) by {aggressorCorpID}[{aggressorAllianceID}]",
    78: "XXX Station state change {solarSystemID}",
    79: "XXX Station conquered {solarSystemID}",
    80: "Station attacked {solarSystemID} ({shieldValue}/{armorValue}/{hullValue}) by {aggressorCorpID}[{aggressorAllianceID}]",
    86: "XXX Territorial Claim Unit under attack {solarSystemID}",
    87: "SBU attacked in {solarSystemID} ({shieldValue}/{armorValue}/{hullValue}) by {aggressorCorpID}[{aggressorAllianceID}]",
    88: "XXX Infrastructure Hub under attack {solarSystemID}",
    93: "Customs Office attacked {planetID} ({shieldLevel}) by {aggressorCorpID}[{aggressorAllianceID}]",
    94: "XXX Customs office has entered reinforced {solarSystemID}",
}
