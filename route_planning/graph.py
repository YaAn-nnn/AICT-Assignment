# Coordinates for heuristic estimation (not real gps)

coordinates = {
    # Central
    "City Hall": (0, 0),
    "Dhoby Ghaut": (-1, 1),
    "Orchard": (-2, 2),
    "Marina Bay": (1, -1),
    "Promenade": (2, -1),
    "Gardens by the Bay": (2, -2),

    # South
    "Outram Park": (-2, -2),
    "Harbourfront": (-3, -2),

    # North
    "Bishan": (0, 4),
    "Caldecott": (1, 5),
    "Serangoon": (2, 5),
    "Stevens": (-2, 3),

    # East
    "Paya Lebar": (4, 1),
    "MacPherson": (3, 2),
    "Tampines": (6, 3),
    "Tanah Merah": (7, 2),
    "Expo": (8, 1),
    "Changi Airport": (9, 0),

    # Future network
    "Sungei Bedok": (7, 3),
    "T5": (10, 1),
    "Punggol": (6, 6),
    "Pasir Ris": (9, 6),
    "Hougang": (4, 6),
    "Ang Mo Kio": (1, 7),
    "Bright Hill": (1, 6),
}

# TODAY MODE GRAPH, estimated timing in minutes between 2 stations

graph_today = {

    # --- EWL Airport Branch ---
    "Changi Airport": [
        ("Expo", 8, "EWL2")
    ],

    "Expo": [
        ("Changi Airport", 8, "EWL2"),
        ("Tanah Merah", 4, "EWL2"),
        ("Tampines", 6, "DTL")
    ],

    # --- EWL Main ---
    "Tanah Merah": [
        ("Expo", 4, "EWL2"),
        ("Paya Lebar", 10, "EWL"),
        ("Tampines", 5, "EWL")
    ],

    "Paya Lebar": [
        ("Tanah Merah", 10, "EWL"),
        ("MacPherson", 3, "CCL"),
        ("City Hall", 12, "EWL"),
        ("Promenade", 10, "CCL"),
    ],

    "Outram Park": [
        ("City Hall", 5, "EWL"),
        ("Orchard", 4, "TEL"),
        ("Dhoby Ghaut", 6, "NEL"),
        ("Marina Bay", 2, "TEL")
    ],

    # --- CCL ---
    "MacPherson": [
        ("Paya Lebar", 3, "CCL"),
        ("Serangoon", 7, "CCL"),
        ("Tampines", 13, "DTL"),
        ("Promenade", 21, "DTL")
    ],

    "Promenade": [
        ("Paya Lebar", 10, "CCL"),
        ("Marina Bay", 4, "CCL"),
        ("MacPherson", 21, "DTL"),
        ("Dhoby Ghaut", 6, "CCL2"),
        ("Stevens", 11, "DTL")
    ],

    "Serangoon": [
        ("Dhoby Ghaut", 13, "NEL"),
        ("MacPherson", 7, "CCL"),
        ("Bishan", 5, "CCL")
    ],

    # --- NSL ---
    "Marina Bay": [
        ("Promenade", 4, "CCL"),
        ("City Hall", 3, "NSL"),
        ("Gardens by the Bay", 3, "TEL"),
        ("Outram Park", 2, "TEL")
    ],

    "City Hall": [
        ("Marina Bay", 3, "NSL"),
        ("Dhoby Ghaut", 2, "NSL"),
        ("Outram Park", 5, "EWL"),
        ("Paya Lebar", 12, "EWL")
    ],

    "Dhoby Ghaut": [
        ("City Hall", 2, "NSL"),
        ("Orchard", 3, "NSL"),
        ("Outram Park", 6, "NEL"),
        ("Serangoon", 13, "NEL"),
        ("Promenade", 6, "CCL2")
    ],

    "Orchard": [
        ("Dhoby Ghaut", 3, "NSL"),
        ("Bishan", 5, "NSL"),
        ("Outram Park", 4, "TEL"),
        ("Stevens", 5, "TEL")
    ],

    "Bishan": [
        ("Orchard", 5, "NSL"),
        ("Caldecott", 4, "CCL"),
        ("Serangoon", 5, "CCL")
    ],

    "Caldecott": [
        ("Bishan", 4, "CCL"),
        ("Stevens", 5, "TEL")
    ],

    # --- DTL ---
    "Tampines": [
        ("Tanah Merah", 5, "EWL"),
        ("MacPherson", 13, "DTL"),
        ("Expo", 6, "DTL")
    ],

    "Gardens by the Bay": [
        ("Marina Bay", 3, "TEL")
    ],

    "Stevens" : [
        ("Promenade", 11, "DTL"),
        ("Orchard", 5, "TEL"),
        ("Caldecott", 5, "TEL")
    ]
}

# FUTURE MODE GRAPH (with T5 + TEL + CRL)

graph_future = {

    # --- TEL (Airport conversion) ---
    "Changi Airport": [
        ("Expo", 8, "TEL"),
        ("Pasir Ris", 18, "CRL"),
        ("T5", 6, "CRL"),
        ("T5", 10, "TEL")
    ],

    "Expo": [
        ("Changi Airport", 8, "TEL"),
        ("Tanah Merah", 4, "TEL"),
        ("Tampines", 6, "DTL"),
        ("Sungei Bedok", 8, "DTL")
    ],

    "Tanah Merah": [
        ("Expo", 4, "TEL"),
        ("Paya Lebar", 10, "EWL"),
        ("Tampines", 5, "EWL"),
    ],

    "Sungei Bedok": [
        ("Gardens by the Bay", 26, "TEL"),
        ("T5", 5, "TEL"),
        ("Expo", 8, "DTL")
    ],

    "T5": [
        ("Sungei Bedok", 5, "TEL"),
        ("Changi Airport", 6, "CRL"),
        ("Changi Airport", 10, "TEL")
    ],

    "Gardens by the Bay": [
        ("Marina Bay", 3, "TEL"),
        ("Sungei Bedok", 26, "TEL")
    ],

    "Stevens": [
        ("Promenade", 11, "DTL"),
        ("Orchard", 5, "TEL"),
        ("Caldecott", 5, "TEL")
    ],

    # --- CRL ---
    "Punggol": [
        ("Pasir Ris", 6, "CRL2"),
        ("Hougang", 8, "NEL")
    ],

    "Hougang": [
        ("Punggol", 8, "NEL"),
        ("Pasir Ris", 10, "CRL"),
        ("Ang Mo Kio", 10, "CRL"),
        ("Serangoon", 4, "NEL")
    ],

    "Pasir Ris": [
        ("Hougang", 10, "CRL"),
        ("Tampines", 6, "EWL"),
        ("Changi Airport", 18, "CRL"),
        ("Punggol", 6, "CRL2")
    ],

    "Ang Mo Kio": [
        ("Hougang", 10, "CRL"),
        ("Bishan", 3, "NSL"),
        ("Bright Hill", 6, "CRL")
    ],

    "Bright Hill": [
        ("Caldecott", 3, "TEL"),
        ("Ang Mo Kio", 6, "CRL")
    ],

    # --- EWL ---
    "Paya Lebar": [
        ("Tanah Merah", 10, "EWL"),
        ("MacPherson", 3, "CCL"),
        ("City Hall", 12, "EWL"),
        ("Promenade", 10, "CCL"),
    ],

    "City Hall": [
        ("Marina Bay", 3, "NSL"),
        ("Dhoby Ghaut", 2, "NSL"),
        ("Outram Park", 5, "EWL"),
        ("Paya Lebar", 12, "EWL")
    ],

    "Outram Park": [
        ("City Hall", 5, "EWL"),
        ("Orchard", 4, "TEL"),
        ("Dhoby Ghaut", 6, "NEL"),
        ("Harbourfront", 3, "NEL"),
        ("Marina Bay", 2, "TEL")
    ],

    "Harbourfront": [
        ("Outram Park", 3, "NEL"),
        ("Marina Bay", 9, "CCL")
    ],

    # --- CCL ---
    "MacPherson": [
        ("Paya Lebar", 3, "CCL"),
        ("Serangoon", 7, "CCL"),
        ("Tampines", 13, "DTL"),
        ("Promenade", 21, "DTL")
    ],

    "Promenade": [
        ("Paya Lebar", 10, "CCL"),
        ("Marina Bay", 4, "CCL"),
        ("MacPherson", 21, "DTL"),
        ("Dhoby Ghaut", 6, "CCL2"),
        ("Stevens", 11, "DTL")
    ],

    "Serangoon": [
        ("MacPherson", 7, "CCL"),
        ("Bishan", 5, "CCL"),
        ("Dhoby Ghaut", 13, "NEL"),
        ("Hougang", 4, "NEL")
    ],

    "Caldecott": [ 
        ("Bishan", 4, "CCL"),
        ("Stevens", 5, "TEL"),
        ("Bright Hill", 3, "TEL")
    ],

    # --- NSL --- 
    "Marina Bay": [
        ("Promenade", 4, "CCL"),
        ("City Hall", 3, "NSL"),
        ("Gardens by the Bay", 3, "TEL"),
        ("Outram Park", 2, "TEL"),
        ("Harbourfront", 9, "CCL")
    ],

    "Dhoby Ghaut": [
        ("City Hall", 2, "NSL"),
        ("Orchard", 3, "NSL"),
        ("Outram Park", 6, "NEL"),
        ("Serangoon", 13, "NEL"),
        ("Promenade", 6, "CCL2")
    ],

    "Orchard": [
        ("Dhoby Ghaut", 3, "NSL"),
        ("Bishan", 5, "NSL"),
        ("Outram Park", 4, "TEL"),
        ("Stevens", 5, "TEL")
    ],

    "Bishan": [
        ("Orchard", 5, "NSL"),
        ("Caldecott", 4, "CCL"),
        ("Serangoon", 5, "CCL"),
        ("Ang Mo Kio", 3, "NSL")
    ],

    # --- DTL ---
    "Tampines": [
        ("Tanah Merah", 5, "EWL"),
        ("Pasir Ris", 6, "EWL"),
        ("MacPherson", 13, "DTL"),
        ("Expo", 6, "DTL"),
    ]
}
