# poketypes/showdown/showdownmessage.py

"""Contains BaseModels for Message parsing and processing.

Remember to use Message.from_message directly, unless you are building test cases where you want to assert that
a given message leads to a certain subclass of Message. `from_message` will auto-detect which MType the given
message corresponds to, and return the associated subclass (or an error detailing what went wrong) for you.
"""

from __future__ import annotations

import json
from enum import Enum, unique
from typing import Dict, List, Optional, Type, Union

from pydantic import BaseModel, Field


@unique
class MType(str, Enum):
    """String-Enum for holding all unique categories of Showdown Generic Messages.

    See https://github.com/smogon/pokemon-showdown/blob/master/PROTOCOL.md for the (partial) list of message types
    """

    empty = ""

    init = "init"
    title = "title"
    users = "users"
    html = "html"
    uhtml = "uhtml"
    uhtmlchange = "uhtmlchange"

    join = "join"
    j = "j"
    J = "J"
    leave = "leave"
    l = "l"  # noqa: E741
    L = "L"
    name = "name"
    n = "n"
    N = "N"
    chat = "chat"
    c = "c"

    notify = "notify"
    battle = "battle"

    # Global messages
    popup = "popup"
    pm = "pm"
    usercount = "usercount"
    nametaken = "nametaken"
    challstr = "challstr"
    updateuser = "updateuser"
    formats = "formats"
    customgroups = "customgroups"
    updatesearch = "updatesearch"
    updatechallenges = "updatechallenges"
    queryreponse = "queryresponse"

    # Tournament messages
    tournament = "tournament"

    # Error states
    unknown = "unknown"


class Message(BaseModel):
    """The base class for all specific Message subclasses to be built from.

    When parsing a string message, you should directly use this class's `from_message` function, which will
    auto-identify which subclass (if any) the given string belongs to.

    Across all Messages, you will be able to access both MTYPE and MESSAGE, though you shouldn't need
    to access MESSAGE directly. (If you do, then we must be missing some data that exists in the raw string)

    Attributes:
        MTYPE: The message type of this message. Must be a vaild showdown general message.
        MESSAGE: The raw message line as sent from showdown. Shouldn't need to be used but worth keeping.
    """

    MTYPE: MType = Field(
        ...,
        description="The message type of this message. Must be a vaild showdown general message.",
    )
    MESSAGE: str = Field(
        ...,
        description="The raw message line as sent from showdown. Shouldn't need to be used but worth keeping.",
    )

    @staticmethod
    def from_message(message: str) -> "Message":
        """Create a specific Message object from a raw string message.

        This is used for general Showdown Messages, compared to the BattleMessage class meant for battle details.

        Args:
            message (str): The newline-stripped single string message as sent by the server.

        Returns:
            Message: An initialized subclass of `Message`, for the corresponding class for this message type.
        """
        try:
            mtype = MType(message.split("|")[1])
            m_class = mtype_to_mclass[mtype]
        except ValueError:
            print(f"Failed to identify which MType we should use for general message key {message.split('|')[1]}.")

            m = Message(MTYPE="unknown", MESSAGE=message)

            return m
        except KeyError:
            print(f"MType {mtype} does not have a class in the dictionary!")

            m = Message(MTYPE="unknown", MESSAGE=message)

            return m

        try:
            m = m_class.from_message(message)
        except NotImplementedError:
            print(f"MType {mtype}'s extraction implementation isn't ready yet!")

            m = Message(MTYPE="unknown", MESSAGE=message)
        except Exception as ex:
            print(f"MType {mtype} failed to build from message {message} due to a(n) {type(ex)}: {ex}")

            m = Message(MTYPE="unknown", MESSAGE=message)

        return m


class Message_init(Message):
    """Message notifying about a battle starting.

    Note: Use Case(s)
        - To communicate battle initialization notice.

    Info: Message Format(s)
        - |init|battle

    Example: Input Example(s)
        - TODO
    """

    def from_message(message: str) -> "Message_init":
        """Create a specific Message object from a raw message."""
        return Message_init(MTYPE=MType.init, MESSAGE=message)


class Message_title(Message):
    """Message notifying about the title of a room.

    Attributes:
        TITLE: The title of this match as shown on pokemon showdown

    Note: Use Case(s)
        - To communicate room title info.

    Info: Message Format(s)
        - |title|TITLE

    Example: Input Example(s)
        - |title|colress-gpt-test1 vs. colress-gpt-test2
    """

    TITLE: str = Field(..., description="The title of this match as shown on pokemon showdown")

    def from_message(message: str) -> "Message_title":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        return Message_title(MTYPE=MType.title, MESSAGE=message, TITLE=m_split[2])


class Message_join(Message):
    """Message containing info about a joining user.

    Attributes:
        USERNAME: The username of the joining player

    Note: Use Case(s)
        - To communicate player room user entry.

    Info: Message Format(s)
        - |join|USERNAME

    Example: Input Example(s)
        - |j|☆colress-gpt-test1
    """

    USERNAME: str = Field(..., description="The username of the joining player")

    def from_message(message: str) -> "Message_join":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        return Message_join(MTYPE=MType.join, MESSAGE=message, USERNAME=m_split[2])


class Message_leave(Message):
    """Message containing info about a leaving user.

    Attributes:
        USERNAME: The username of the leaving player

    Note: Use Case(s)
        - To communicate player room user exit.

    Info: Message Format(s)
        - |leave|USERNAME
        - |l|USERNAME

    Example: Input Example(s)
        - |l|☆colress-gpt-test1
    """

    USERNAME: str = Field(..., description="The username of the leaving player")

    def from_message(message: str) -> "Message_leave":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        return Message_leave(MTYPE=MType.leave, MESSAGE=message, USERNAME=m_split[2])


class UserSettings(BaseModel):
    """A helper class to contain information about user settings.

    Attributes:
        BLOCK_CHALLENGES: Whether you are currently blocking challenges
        BLOCK_PMS: Whether you are currently blocking PMs
        IGNORE_TICKETS: Whether you are currently ignoring tickets
        HIDE_BATTLES: Whether you are currently hiding battles on your trainer card
        BLOCK_INVITES: Whether you are currently blocking invites
        DO_NOT_DISTURB: Your current do not disturb setting
        BLOCK_FRIEND_REQUESTS: Whether you are currently blocking friend requests
        ALLOW_FRIEND_NOTIFICATIONS: Whether you are currently allowing friend notifications
        DISPLAY_BATTLES: Whether you are currently displaying battles to friends
        HIDE_LOGINS: Whether you are currently hiding logins
        HIDDEN_NEXT_BATTLE: Whether you are hiding your next battle or not
        INVITE_ONLY_NEXT_BATTLE: Whether you are limiting your next battle to invite only or not
        LANGUAGE: The language set by your user
    """

    BLOCK_CHALLENGES: bool = Field(..., description="Whether you are currently blocking challenges")
    BLOCK_PMS: bool = Field(..., description="Whether you are currently blocking PMs")
    IGNORE_TICKETS: bool = Field(..., description="Whether you are currently ignoring tickets")
    HIDE_BATTLES: bool = Field(..., description="Whether you are currently hiding battles on your trainer card")
    BLOCK_INVITES: bool = Field(..., description="Whether you are currently blocking invites")
    DO_NOT_DISTURB: bool = Field(..., description="Your current do not disturb setting")
    BLOCK_FRIEND_REQUESTS: bool = Field(..., description="Whether you are currently blocking friend requests")
    ALLOW_FRIEND_NOTIFICATIONS: bool = Field(..., description="Whether you are currently allowing friend notifications")
    DISPLAY_BATTLES: bool = Field(..., description="Whether you are currently displaying battles to friends")
    HIDE_LOGINS: bool = Field(..., description="Whether you are currently hiding logins")
    HIDDEN_NEXT_BATTLE: bool = Field(..., description="Whether you are hiding your next battle or not")
    INVITE_ONLY_NEXT_BATTLE: bool = Field(
        ..., description="Whether you are limiting your next battle to invite only or not"
    )

    LANGUAGE: Optional[str] = Field(None, description="The language set by your user")


class Message_updateuser(Message):
    """Message containing info about your user settings / login information.

    Attributes:
        USERNAME: The username of your current login
        NAMED: Whether you are currently logged in or not
        AVATAR: Either a number id of the user's avatar or a custom value
        SETTINGS: The user settings for your current user session

    Note: Use Case(s)
        - To communicate any changes to your login / user session.

    Info: Message Format(s)
        - |updateuser|USER|NAMED|AVATAR|SETTINGS

    Example: Input Example(s)
        - TODO
    """

    USERNAME: str = Field(..., description="The username of your current login")

    NAMED: bool = Field(..., description="Whether you are currently logged in or not")
    AVATAR: Union[int, str] = Field(..., description="Either a number id of the user's avatar or a custom value")

    SETTINGS: UserSettings = Field(..., description="The user settings for your current user session")

    def from_message(message: str) -> "Message_updateuser":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        uname = m_split[2]
        named = bool(int(m_split[3]))
        avatar = m_split[4]

        u_set_json = json.loads(m_split[5])
        u_set = UserSettings(
            BLOCK_CHALLENGES=u_set_json["blockChallenges"],
            BLOCK_PMS=u_set_json["blockPMs"],
            IGNORE_TICKETS=u_set_json["ignoreTickets"],
            HIDE_BATTLES=u_set_json["hideBattlesFromTrainerCard"],
            BLOCK_INVITES=u_set_json["blockInvites"],
            DO_NOT_DISTURB=u_set_json["doNotDisturb"],
            BLOCK_FRIEND_REQUESTS=u_set_json["blockFriendRequests"],
            ALLOW_FRIEND_NOTIFICATIONS=u_set_json["allowFriendNotifications"],
            DISPLAY_BATTLES=u_set_json["displayBattlesToFriends"],
            HIDE_LOGINS=u_set_json["hideLogins"],
            HIDDEN_NEXT_BATTLE=u_set_json["hiddenNextBattle"],
            INVITE_ONLY_NEXT_BATTLE=u_set_json["inviteOnlyNextBattle"],
            LANGUAGE=u_set_json["language"],
        )

        return Message_updateuser(
            MTYPE=MType.updateuser, MESSAGE=message, USERNAME=uname, NAMED=named, AVATAR=avatar, SETTINGS=u_set
        )


class Message_formats(Message):
    """Message containing info about server enabled formats.

    Attributes:
        FORMATS: The list of formats

    Note: Use Case(s)
        - To communicate all available formats the user can play

    Info: Message Format(s)
        - |formats|FORMATSLIST

    Example: Input Example(s)
        - TODO
    """

    FORMATS: List[str] = Field(..., description="The list of formats")

    def from_message(message: str) -> "Message_formats":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        formats = []
        for fs in m_split[2:]:
            if fs[0] == ",":
                continue

            formats.append(fs.split(",")[0])

        return Message_formats(MTYPE=MType.formats, MESSAGE=message, FORMATS=formats)


class CustomGroup(BaseModel):
    """A helper class to contain information about server custom groups."""

    SYMBOL: str = Field(..., description="The symbol used before users of this group")
    NAME: Optional[str] = Field(..., description="The name of the group")
    # TODO: Add validator for the valid types of groups
    TYPE: str = Field(..., description="The category of this group")


class Message_customgroups(Message):
    """Message containing info about server custom groups.

    Attributes:
        CUSTOM_GROUPS: The list of custom groups

    Note: Use Case(s)
        - To communicate all usergroups

    Info: Message Format(s)
        - |customgroups|CUSTOMGROUPS

    Example: Input Example(s)
        - TODO
    """

    CUSTOM_GROUPS: List[CustomGroup] = Field(..., description="The list of custom groups")

    def from_message(message: str) -> "Message_customgroups":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        groups = json.loads(m_split[2])

        cgs = []
        for g in groups:
            cg = CustomGroup(SYMBOL=g["symbol"], NAME=g["name"], TYPE=g["type"])
            cgs.append(cg)

        return Message_customgroups(MTYPE=MType.customgroups, MESSAGE=message, CUSTOM_GROUPS=cgs)


class Message_challstr(Message):
    """Message containing a login challenge string.

    Attributes:
        CHALLSTR: The string challenge string

    Note: Use Case(s)
        - Gives the user a challenge string to submit to the login server to get a token

    Info: Message Format(s)
        - |challstr|CHALLSTR

    Example: Input Example(s)
        - TODO
    """

    CHALLSTR: str = Field(..., description="The string challenge string")

    def from_message(message: str) -> "Message_challstr":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        chall = "|".join(m_split[2:])

        return Message_challstr(MTYPE=MType.challstr, MESSAGE=message, CHALLSTR=chall)


class Message_updatesearch(Message):
    """Message containing a current ladder searches, if any.

    Attributes:
        SEARCHING: A list of formats currently searching for a ladder match
        GAMES: A optional dictionary of game-id->format of currently ongoing games

    Note: Use Case(s)
        - Gives the user an update about all of their current battle search requests.

    Info: Message Format(s)
        - |updatesearch|JSON

    Example: Input Example(s)
        - TODO
    """

    SEARCHING: List[str] = Field(..., description="A list of formats currently searching for a ladder match")
    GAMES: Optional[Dict[str, str]] = Field(
        ..., description="A optional dictionary of game-id->format of currently ongoing games"
    )

    def from_message(message: str) -> "Message_updatesearch":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        data = json.loads(m_split[2])

        searching = data["searching"]
        games = data["games"]

        return Message_updatesearch(MTYPE=MType.updatesearch, MESSAGE=message, SEARCHING=searching, GAMES=games)


class Message_updatechallenges(Message):
    """Message containing a current challenge searches, if any.

    Attributes:
        OUTGOING: A dictionary of username->format for each outgoing challenge
        INCOMING: A dictionary of username->format for each incoming challenge

    Note: Use Case(s)
        - Gives the user an update about all of their current battle challenge requests.

    Info: Message Format(s)
        - |updatechallenges|JSON

    Example: Input Example(s)
        - TODO
    """

    OUTGOING: Dict[str, str] = Field({}, description="A dictionary of username->format for each outgoing challenge")
    INCOMING: Dict[str, str] = Field({}, description="A dictionary of username->format for each incoming challenge")

    def from_message(message: str) -> "Message_updatechallenges":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        data = json.loads(m_split[2])

        incoming = data["challengesFrom"]

        if data.get("challengesTo", None) is not None:
            outgoing = {chal["to"]: chal["format"] for chal in data["challengesTo"]}
        else:
            outgoing = {}

        return Message_updatechallenges(
            MTYPE=MType.updatechallenges, MESSAGE=message, OUTGOING=outgoing, INCOMING=incoming
        )


class Message_pm(Message):
    """Message containing a PM to/from the user.

    Attributes:
        SOURCE: The username of the user who sent the pm
        TARGET: The username of the user who received the pm
        PM: The message. Newlines are denoted with |
        IS_CHALLENGE: Whether this PM is a challenge to a battle
        CHALLENGE_FORMAT: The format of the challenge if it is a challenge

    Note: Use Case(s)
        - Notify the user about a PM received.

    Info: Message Format(s)
        - |pm|SOURCE|TARGET|PM

    Example: Input Example(s)
        - TODO
    """

    SOURCE: str = Field(..., description="The username of the user who sent the pm")
    TARGET: str = Field(..., description="The username of the user who received the pm")

    PM: str = Field(..., description="The message. Newlines are denoted with |")

    IS_CHALLENGE: bool = Field(False, description="Whether this PM is a challenge to a battle")
    CHALLENGE_FORMAT: Optional[str] = Field(None, description="The format of the challenge if it is a challenge")

    def from_message(message: str) -> "Message_pm":
        """Create a specific Message object from a raw message."""
        m_split = message.split("|")

        source = m_split[2].strip()
        target = m_split[3].strip()

        message = "|".join(m_split[4:])

        is_chal = len(message) >= 10 and message[:10] == "/challenge"
        if is_chal and len(message) > 10:
            chal_format = m_split[5]
        else:
            chal_format = None

        return Message_pm(
            MTYPE=MType.pm,
            MESSAGE=message,
            SOURCE=source,
            TARGET=target,
            PM=message,
            IS_CHALLENGE=is_chal,
            CHALLENGE_FORMAT=chal_format,
        )


mtype_to_mclass: Dict[MType, Type["Message"]] = {
    MType.init: Message_init,
    MType.title: Message_title,
    MType.j: Message_join,
    MType.join: Message_join,
    MType.J: Message_join,
    MType.l: Message_leave,
    MType.leave: Message_leave,
    MType.L: Message_leave,
    MType.formats: Message_formats,
    MType.customgroups: Message_customgroups,
    MType.challstr: Message_challstr,
    MType.updatesearch: Message_updatesearch,
    MType.updateuser: Message_updateuser,
    MType.updatechallenges: Message_updatechallenges,
    MType.pm: Message_pm,
}
