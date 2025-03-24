# lobby_table_handler.py

from src.backend.data_structures import player_dict, table_dict

lobby_list = []  # List to store players in the lobby
table_list = []  # List to store tables

def connect_player(token):
    """
    If token valid, add player to lobbylist
    Else: tell the player to login
    """
    # TODO: Implement token validation
    if token:
        lobby_list.append(token)  # Assuming token is the player identifier
        return True
    else:
        return False

def login_player(name):
    """
    Consistency check, whether name is unique
    Create token for player
    Create dict for player
    Add player_dict to lobby list
    """
    # TODO: Implement name uniqueness check
    token = generate_token()  # Implement token generation
    player = player_dict.copy()
    player["name"] = name
    player["uuid"] = token
    lobby_list.append(player)
    return player

def create_table(name, rounds):
    """
    Create table dict
    change status to running
    Add table_dict to lobby
    """
    table = table_dict.copy()
    table["tablename"] = name
    table["rounds"] = rounds
    table["status"] = "open"
    table_list.append(table)
    return table

def add_player_to_table(table, player_name):
    """
    Check for max of 4 players
    Else: add player to table
    """
    if len(table["players"]) < 4:
        table["players"].append(player_name)
        return True
    else:
        return False

def start_table(table):
    """
    Check if player is sitting at the table
    Consistency check: are four players at the table
    Change mode to running mode
    Assign a game_dict to the table
    Call init_game function -> todo
    """
    # TODO: Implement player sitting at the table check
    if len(table["players"]) == 4:
        table["status"] = "running"
        # TODO: Assign a game_dict to the table
        # TODO: Call init_game function
        return True
    else:
        return False

def generate_token():
    """
    Generate a unique token for the player
    """
    # TODO: Implement token generation logic
    return "token"  # Placeholder token
