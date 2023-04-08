CREATE TABLE IF NOT EXISTS guilds (
        GuildID integer PRIMARY KEY,
        Prefix text DEFAULT "+"
);

CREATE TABLE IF NOT EXISTS exp (
        UserID integer,
        GuildID integer,
        XP integer DEFAULT 0,
        Level integer DEFAULT 0,
        XPLock text DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lvl_rewards (
        RoleID integer PRIMARY KEY,
        GuildID integer,
        lvl integer
);

CREATE TABLE IF NOT EXISTS modmail (
        GuildID integer,
        MessageID integer,
        submit_channel integer,
        Apply_Name text,
        Emoji integer,
        Questions text
);

CREATE TABLE IF NOT EXISTS modmail_submissions (
        GuildID integer,
        MessageID integer,
        ApplicantID integer,
        Application_Name text
);

CREATE TABLE IF NOT EXISTS roster (
        GuildID integer PRIMARY KEY,
        RoleIDs integer,
        ChannelID integer,
        MessageID integer
);

CREATE TABLE IF NOT EXISTS mutes (
        UserID integer PRIMARY KEY,
        GuildID integer,
        EndTime text,
        Reason text
);

CREATE TABLE IF NOT EXISTS warns (
        UserID integer,
        GuildID integer,
        EndTime text,
        Reason text,
        Counter integer
);

CREATE TABLE IF NOT EXISTS muterole (
        GuildID integer PRIMARY KEY,
        RoleID integer
);

CREATE TABLE IF NOT EXISTS starboard (
        RootMessageID integer PRIMARY KEY,
        StarMessageID integer,
        Stars integer DEFAULT 1
);

CREATE TABLE IF NOT EXISTS message_log (
        GuildID integer PRIMARY KEY,
        message_log_channel integer
);

CREATE TABLE IF NOT EXISTS role_log (
        GuildID integer PRIMARY KEY,
        role_log_channel integer
);

CREATE TABLE IF NOT EXISTS nickname_log (
        GuildID integer PRIMARY KEY,
        nickname_log_channel integer
);

CREATE TABLE IF NOT EXISTS mod_log (
        GuildID integer PRIMARY KEY,
        mod_log_channel integer
);

CREATE TABLE IF NOT EXISTS customcommands (
        GuildID integer,
        Commandname text,
        Content text
);

CREATE TABLE IF NOT EXISTS welcomer (
        GuildID integer PRIMARY KEY,
        ChannelID integer,
        welcome_message text
);

CREATE TABLE IF NOT EXISTS dmwelcomer (
        GuildID integer PRIMARY KEY,
        welcome_message text
);

CREATE TABLE IF NOT EXISTS join_to_create_channels (
        GuildID integer PRIMARY KEY,
        ChannelID integer
);

CREATE TABLE IF NOT EXISTS join_to_create_user_channels (
        GuildID integer,
        ChannelID integer
);
