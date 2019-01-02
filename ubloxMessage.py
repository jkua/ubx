import struct
import logging
import datetime

SYNC1=0xb5
SYNC2=0x62

CLASS = {
    "NAV" : 0x01,
    "RXM" : 0x02,
    "INF" : 0x04,
    "ACK" : 0x05,
    "CFG" : 0x06,
    "UPD" : 0x09,
    "MON" : 0x0a,
    "AID" : 0x0b,
    "TIM" : 0x0d,
    "USR" : 0x40,
    "ESF" : 0x10,
    "MGA" : 0x13
}

CLIDPAIR = {
    "ACK-ACK" : (0x05, 0x01),
    "ACK-NACK" : (0x05, 0x00),
    "AID-ALM" : (0x0b, 0x30),
    "AID-DATA" : (0x0b, 0x10),
    "AID-EPH" : (0x0b, 0x31),
    "AID-HUI" : (0x0b, 0x02),
    "AID-INI" : (0x0b, 0x01),
    "AID-REQ" : (0x0b, 0x00),
    "AID-UNKNOWN-0x32" : (0x0b, 0x32),
    "AID-UNKNOWN-0x50" : (0x0b, 0x50),
    "AID-REQ" : (0x0b, 0x00),
    "CFG-ANT" : (0x06, 0x13),
    "CFG-CFG" : (0x06, 0x09),
    "CFG-DAT" : (0x06, 0x06),
    "CFG-EKF" : (0x06, 0x12),
    "CFG-FXN" : (0x06, 0x0e),
    "CFG-GNSS" : (0x06, 0x3e),
    "CFG-HNR" : (0x06, 0x5c),
    "CFG-INF" : (0x06, 0x02),
    "CFG-LIC" : (0x06, 0x80),
    "CFG-MSG" : (0x06, 0x01),
    "CFG-NAV2" : (0x06, 0x1a),
    "CFG-NMEA" : (0x06, 0x17),
    "CFG-PMS" : (0x06, 0x86),
    "CFG-PRT" : (0x06, 0x00),
    "CFG-RATE" : (0x06, 0x08),
    "CFG-RST" : (0x06, 0x04),
    "CFG-RXM" : (0x06, 0x11),
    "CFG-SBAS" : (0x06, 0x16),
    "CFG-TM" : (0x06, 0x10),
    "CFG-TM2" : (0x06, 0x19),
    "CFG-TMODE" : (0x06, 0x1d),
    "CFG-TP" : (0x06, 0x07),
    "CFG-USB" : (0x06, 0x1b),
    "ESF-INS" : (0x10, 0x15),
    "ESF-MEAS" : (0x10, 0x02),
    "ESF-RAW" : (0x10, 0x03),
    "ESF-STATUS" : (0x10, 0x10),
    "HNR-PVT" : (0x28, 0x00),
    "INF-DEBUG" : (0x04, 0x04),
    "INF-ERROR" : (0x04, 0x00),
    "INF-NOTICE" : (0x04, 0x02),
    "INF-TEST" : (0x04, 0x03),
    "INF-USER" : (0x04, 0x07),
    "INF-WARNING" : (0x04, 0x01),
    "LOG-FINDTIME" : (0x21, 0x0e),
    "LOG-RETRIEVEPOS" : (0x21, 0x0b),
    "LOG-RETRIEVEPOSEXTRA" : (0x21, 0x0f),
    "LOG-RETRIEVESTRING" : (0x21, 0x0d),
    "MGA-ACK" : (0x13, 0x60),
    "MGA-DBD" : (0x13, 0x80),
    "MGA-FLASH" : (0x13, 0x21),
    "MGA-GPS-EPH" : (0x13, 0x00),
    "MGA-GPS-ALM" : (0x13, 0x00),
    "MGA-GLO-EPH" : (0x13, 0x06),
    "MGA-GLO-ALM" : (0x13, 0x06),
    "MGA-INI-TIME_UTC" : (0x13, 0x40),
    "MON-EXCEPT" : (0x0a, 0x05),
    "MON-HW" : (0x0a, 0x09),
    "MON-IO" : (0x0a, 0x02),
    "MON-IPC" : (0x0a, 0x03),
    "MON-MSGPP" : (0x0a, 0x06),
    "MON-RXBUF" : (0x0a, 0x07),
    "MON-SCHD" : (0x0a, 0x01),
    "MON-SMGR" : (0x0a, 0x2e),
    "MON-TXBUF" : (0x0a, 0x08),
    "MON-USB" : (0x0a, 0x0a),
    "MON-VER" : (0x0a, 0x04),
    "NAV-ATT" : (0x01, 0x05),
    "NAV-CLOCK" : (0x01, 0x22),
    "NAV-DGPS" : (0x01, 0x31),
    "NAV-DOP" : (0x01, 0x04),
    "NAV-EKFSTATUS" : (0x01, 0x40),
    "NAV-HPPOSECEF" : (0x01, 0x13),
    "NAV-HPPOSLLH" : (0x01, 0x14),
    "NAV-POSECEF" : (0x01, 0x01),
    "NAV-POSLLH" : (0x01, 0x02),
    "NAV-POSUTM" : (0x01, 0x08),
    "NAV-PVT" : (0x01, 0x07),
    "NAV-RELPOSNED" : (0x01, 0x3c),
    "NAV-SBAS" : (0x01, 0x32),
    "NAV-SOL" : (0x01, 0x06),
    "NAV-STATUS" : (0x01, 0x03),
    "NAV-SVIN" : (0x01, 0x3b),
    "NAV-SVINFO" : (0x01, 0x30),
    "NAV-TIMEGPS" : (0x01, 0x20),
    "NAV-TIMEUTC" : (0x01, 0x21),
    "NAV-VELECEF" : (0x01, 0x11),
    "NAV-VELNED" : (0x01, 0x12),
    "RXM-ALM" : (0x02, 0x30),
    "RXM-EPH" : (0x02, 0x31),
    "RXM-POSREQ" : (0x02, 0x40),
    "RXM-PMREQ" : (0x02, 0x41),
    "RXM-RAW" : (0x02, 0x10),
    "RXM-RAWX" : (0x02, 0x15),
    "RXM-RTCM" : (0x02, 0x32),
    "RXM-SFRB" : (0x02, 0x11),
    "RXM-SFRBX" : (0x02, 0x13),
    "RXM-SVSI" : (0x02, 0x20),
    "SEC-SIGN" : (0x27, 0x01),
    "SEC-UNIQID" : (0x27, 0x03),
    "TIM-DOSC" : (0x0d, 0x11),
    "TIM-FCHG" : (0x0d, 0x16),
    "TIM-SMEAS" : (0x0d, 0x13),
    "TIM-SVIN" : (0x0d, 0x04),
    "TIM-TM" : (0x0d, 0x02),
    "TIM-TM2" : (0x0d, 0x03),
    "TIM-TOS" : (0x0d, 0x12),
    "TIM-TP" : (0x0d, 0x01),
    "TIM-VCOCAL" : (0x0d, 0x15),
    "UPD-DOWNL" : (0x09, 0x01),
    "UPD-EXEC" : (0x09, 0x03),
    "UPD-MEMCPY" : (0x09, 0x04),
    "UPD-SOS" : (0x09, 0x14),
    "UPD-UPLOAD" : (0x09, 0x02),
    "NMEA-DTM" : (0xf0, 0x0a),
    "NMEA-GBS" : (0xf0, 0x09),
    "NMEA-GGA" : (0xf0, 0x00),
    "NMEA-GLL" : (0xf0, 0x01),
    "NMEA-GNS" : (0xf0, 0x0d),
    "NMEA-GRS" : (0xf0, 0x06),
    "NMEA-GSA" : (0xf0, 0x02),
    "NMEA-GST" : (0xf0, 0x07),
    "NMEA-GSV" : (0xf0, 0x03),
    "NMEA-RMC" : (0xf0, 0x04),
    "NMEA-VTG" : (0xf0, 0x05),
    "NMEA-ZDA" : (0xf0, 0x08),
    "NMEAP-UNKNOWN-0x01" : (0xf1, 0x01),
    "NMEAP-TIME" : (0xf1, 0x04),
    "NMEAP-CONFIG" : (0xf1, 0x41),
    "RTCM-BEIMSM4" : (0xf5, 0x7c),
    "RTCM-BEIMSM7" : (0xf5, 0x7f),
    "RTCM-GPSMSM4" : (0xf5, 0x4a),
    "RTCM-GPSMSM7" : (0xf5, 0x4d),
    "RTCM-GLOCODE" : (0xf5, 0xe6),
    "RTCM-GLOMSM4" : (0xf5, 0x54),
    "RTCM-GLOMSM7" : (0xf5, 0x57),
    "RTCM-REFSTATIONARP" : (0xf5, 0x05),
    "RTCM-REFSTATIONPVT" : (0xf5, 0xfe),

}

CLIDPAIR_INV = dict( [ [v,k] for k,v in CLIDPAIR.items() ] )

# MSGFMT - Describes the format of each message. 
# The key tuple contains the name of the message and the size in bytes. 
# If the size is None, than than this is a variable length message.
#
# The value of each dictionary item is in one of two formats. Both are lists.
#
# In the first format, the first element of the list is a string describing the
# struct format (see the Python struct documentation). The second element is a
# list of strings with field names for each of the elements of the struct.
#
# The second format is used if there is a header section followed by repeated
# sections. In this format, the first element is the number of bytes for the 
# header section, followed by the struct format, then the field names. 
#
# The fourth element is where the description of the repeated section starts. As 
# with the header section, this begins with the number of bytes for each 
# section. It is not the sum of the section sizes. So if each repeated section 
# is 12 bytes, this value is 12. Finally, the last (sixth) element is the list
# of field names.

MSGFMT = {
    ("NAV-POSECEF", 20) :
        ["<IiiiI", ["ITOW", "ECEF_X", "ECEF_Y", "ECEF_Z", "Pacc"]],
    ("NAV-POSLLH", 28) :
        ["<IiiiiII", ["ITOW", "LON", "LAT", "HEIGHT", "HMSL", "Hacc", "Vacc"]],
    ("NAV-POSUTM", 18) :
        ["<Iiiibb", ["ITOW", "EAST", "NORTH", "ALT", "ZONE", "HEM"]],
    ("NAV-DOP", 18) :
        ["<IHHHHHHH", ["ITOW", "GDOP", "PDOP", "TDOP", "VDOP", "HDOP", "NDOP", "EDOP"]],
    ("NAV-STATUS", 16) :
        ["<IBBBxII", ["ITOW", "GPSfix", "Flags", "DiffS", "TTFF", "MSSS"]],
    ("NAV-SOL", 52) :
        ["<IihBBiiiIiiiIHxBxxxx", ["ITOW", "Frac", "week", "GPSFix", "Flags", "ECEF_X", "ECEF_Y", "ECEF_Z", "Pacc",
         "ECEFVX", "ECEFVY", "ECEFVZ", "SAcc", "PDOP", "numSV"]],
    ("NAV-VELECEF", 20) :
        ["<IiiiI", ["ITOW", "ECEFVX", "ECEFVY", "ECEFVZ", "SAcc"]],
    ("NAV-VELNED", 36) :
        ["<IiiiIIiII", ["ITOW", "VEL_N", "VEL_E", "VEL_D", "Speed", "GSpeed", "Heading", "SAcc", "CAcc"]],
    ("NAV-TIMEGPS", 16) :
        ["<IihbBI", ["ITOW", "Frac", "week", "LeapS", "Valid", "TAcc"]],
    ("NAV-TIMEUTC", 20) :
        ["<IIiHBBBBBB", ["ITOW", "TAcc", "Nano", "Year", "Month", "Day", "Hour", "Min", "Sec", "Valid"]],
    ("NAV-CLOCK",  20) :
        ["<IiiII", ["ITOW", "CLKB", "CLKD", "TAcc", "FAcc"]],
    ("NAV-SVINFO", None) :
        [8, "<IBxxx", ["ITOW", "NCH"], 12, "<BBBbBbhi", ["chn", "SVID", "Flags", "QI", "CNO", "Elev", "Azim", "PRRes"]],
    ("NAV-DGPS", None) :
        [16, "<IihhBBxx", ["ITOW", "AGE", "BASEID", "BASEHLTH", "NCH", "STATUS"], 12, "<BBHff", ["SVID", "Flags", "AGECH", "PRC", "PRRC"]],
    ("NAV-SBAS", None) :
        [12, "<IBBbBBxxx", ["ITOW", "GEO", "MODE", "SYS", "SERVICE", "CNT"], 12, "<BBBBBxhxxh", ["SVID", "FLAGS", "UDRE", "SYSn", "SERVICEn", "PRC", "IC"]],
    ("NAV-EKFSTATUS", 36) : # no response to query
        ["<iiIhbbiiihhhbB", ["pulses", "period", "gyromean", "temp", "dir", "calib", "pulse", "gbias", "gscale", "accps", "accgb", "accgs", "used", "res"]],
    ("NAV-ATT", 32) :
        ["<IBxxxiiiIII", ["ITOW", "Version", "Roll", "Pitch", "Heading", "AccRoll", "AccPitch", "AccHeading"]],
    ("NAV-PVT", 92) :
        ["<IHBBBBBBIiBBBBiiiiIIiiiiiIIHxxxxxxihH", ["ITOW", "Year", "Month", "Day", "Hour", "Min", "Sec", "Valid", "TAcc", "Nano", "FixType", "Flags", "Flags2", "NumSV", "LON", "LAT", "HEIGHT", "HMSL", "Hacc", "Vacc", "VEL_N", "VEL_E", "VEL_D", "GSpeed", "HeadMot", "SAcc", "HeadAcc", "PDOP", "HeadVeh", "MagDec", "MagAcc"]],
    # ('RXM-RAW', [{'Week': 1575, 'ITOW': 475184470, 'NSV': 0}])
    ("RXM-RAW", None) :
        [8, "<ihBx", ["ITOW", "Week", "NSV"], 24, "<ddfBbbB", ["CPMes", "PRMes", "DOMes", "SV", "MesQI", "CNO", "LLI"]],
    ("RXM-RAWX", None) :
        [16, "<dHbBBxxx", ["RCVTOW", "Week", "LeapS", "NumMeas", "RecStat"], 32, "<ddfBBxBHBBBBBx", ["PRMes", "CPMes", "DOMes", "GNSSID", "SVID", "FreqId", "LockTime", "CNO", "PRStdev", "CPStdev", "DOStdev", "TrkStat"]],
    ("RXM-SVSI", None) :
        [8, "<ihBB", ["ITOW", "Week", "NumVis", "NumSv"], 6, "<BBhbB", ["SVID", "SVFlag", "Azim", "Elev", "Age"]],
    ("RXM-SFRB", 42) :
        ["<BBiiiiiiiiii", ["CHN", "SVID", "DWRD0", "DWRD1", "DWRD2", "DWRD3", "DWRD4", "DWRD5", "DWRD6", "DWRD7", "DWRD8", "DWRD9"]],
    ("RXM-SFRBX", None) :
        [8, "<BBxBBBBx", ["GNSSID", "SVID", "FreqId", "NumWords", "CHN", "Version"], 4, "<I", ["DWRD"]],
    ("RXM-ALM", 1) :
        ["<B", ["SVID"]],
    ("RXM-ALM", 8)  :
        ["<II", ["SVID", "WEEK"]],
    ("RXM-ALM", 40) :
        ["<" + "I"*10, ["SVID", "WEEK", "DWRD0", "DWRD1", "DWRD2", "DWRD3", "DWRD4", "DWRD5", "DWRD6", "DWRD7"]],
    ("RXM-EPH", 1) :
        ["<B", ["SVID"]],
    ("RXM-EPH", 8) :
        ["<II", ["SVID", "HOW"]],
    ("RXM-EPH", 104) :
        ["<" + "I"*26, ["SVID", "HOW", "SF1D0", "SF1D1", "SF1D2", "SF1D3", "SF1D4",
            "SF1D5", "SF1D6", "SF1D7", "SF2D0", "SF2D1", "SF2D2", "SF2D3", "SF2D4",
            "SF2D5", "SF2D6", "SF2D7", "SF3D0", "SF3D1", "SF3D2", "SF3D3", "SF3D4", "SF3D5", "SF3D6", "SF3D7"]],
    ("RXM-PMREQ", 8) :
        ["<II", ["duration", "flags"]],
    ("RXM-PMREQ", 16) :
        ["<BxxxIII", ["version", "duration", "flags", "wakeupSources"]],
    ("INF-ERROR", None) :
        [0, "", [], 1, "c", ["Char"]],
    ("INF-WARNING", None) :
        [0, "", [], 1, "c", ["Char"]],
    ("INF-NOTICE", None) :
        [0, "", [], 1, "c", ["Char"]],
    ("INF-TEST", None) :
        [0, "", [], 1, "c", ["Char"]],
    ("INF-DEBUG", None) :
       [0, "", [], 1, "c", ["Char"]],
    ("INF-USER", None) :
        [0, "", [], 1, "c", ["Char"]],
    ("ACK-ACK", 2) :
        ["<BB", ["ClsID", "MsgID"]],
    ("ACK-NACK", 2) :
        ["<BB", ["ClsID", "MsgID"]],
    ("CFG-GNSS", None) :
        [4, "<BBBB", ['msgVer', 'numTrkChHw', 'numTrkChUse', 'numConfigBlocks'], 8, "<BBBBL", ['gnssId', 'resTrkCh', 'maxTrkCh', 'reserved1', 'flags']],
    ("CFG-PRT", 1) :
        ["<B", ["PortID"]],
    ("CFG-PRT", None) :
        [0, "", [], 20, "<BxHIIHHHxx", ["PortID", "TxReady", "Mode", "Baudrate", "In_proto_mask", "Out_proto_mask", "Flags"]],
    ("CFG-USB", 108) :
        ["<HHxxHHH32s32s32s", ["VendorID", "ProductID", "reserved2", "PowerConsumption", "Flags", "VendorString", "ProductString", "SerialNumber"]],
    ("CFG-MSG", 2) :
        ["<BB", ["msgClass", "msgId"]],
    ("CFG-MSG", 3) :
        ["<BBB", ["msgClass", "msgId", "rate"]],
    ("CFG-MSG", None) :
        [2, "<BB", ["msgClass", "msgId"], 1, "B", ['rate']],
    ("CFG-NMEA", 4) :
        ["<BBBB", ["Filter", "Version", "NumSV", "Flags"]],
    ("CFG-PMS", 8) :
        ["<BBHHxx", ["Version", "PowerSetupValue", "Period", "OnTime"]],
    ("CFG-RATE", 6) :
        ["<HHH", ["Meas", "Nav", "Time"]],
    ("CFG-CFG", 12) :
        ["<III", ["clearMask", "saveMask", "loadMask"]],
    ("CFG-TP", 20) :
        ["<IIbBxxhhi", ["interval", "length", "status", "time_ref", "antenna_cable_delay", "RF_group_delay", "user_delay"]],
    ("CFG-NAV2", 40) :
        ["<BxxxBBBBiBBBBBBxxHHHHBxxxxxxxxxxx", ["Platform", "MinSVInitial", "MinSVs", "MaxSVs", "FixMode",
         "FixedAltitude", "MinCN0Initial", "MinCN0After", "MinELE", "DGPSTO", "MaxDR", "NAVOPT", "PDOP",
         "TDOP", "PACC", "TACC", "StaticThres"]],
# CFG DAT - Get/Set current Datum
    ("CFG-INF", 1) :
        ["<B", ["ProtocolID"]],
    ("CFG-INF", None) :
        [0, "", [], 10, "<BxxxBBBBBB", ["ProtocolID", "INFMSG_mask0", "INFMSG_mask1", "INFMSG_mask2", "INFMSG_mask3", "INFMSG_mask4", "INFMSG_mask5"]],
    ("CFG-RST", 4) :
        ["<HBx", ["nav_bbr", "Reset"]],
    ("CFG-RXM", 2) :
        ["<BB", ["gps_mode", "lp_mode"]],
    ("CFG-ANT", 4) :
        ["<HH", ["flags", "pins"]],
    ("CFG-FXN", 36) :
        ["<IIIIIIIxxxxI", ["flags", "t_reacq", "t_acq", "t_reacq_off", "t_acq_off", "t_on", "t_off", "base_tow"]],
    ("CFG-SBAS", 8) :
        ["<BBBxI", ["mode", "usage", "maxsbas", "scanmode"]],
    ("CFG-LIC", 12) :
        ["<HHHHHH", ["lic1", "lic2", "lic3", "lic4", "lic5", "lic6"]],
    ("CFG-TM", 12) :
        ["<III", ["INTID", "RATE", "FLAGS"]],
    ("CFG-TM2", 1) :
        ["<B", ["CH"]],
    ("CFG-TM2", 12) :
        ["<BxxxII", ["CH", "RATE", "FLAGS"]],
    ("CFG-TMODE", 28) :
        ["<IiiiIII", ["TimeMode", "FixedPosX", "FixedPosY", "FixedPosZ", "FixedPosVar", "SvinMinDur", "SvinVarLimit"]],
    ("CFG-HNR", 4) :
        ["<Bxxx", ['HighNavRate']],
# CFG EKF - Dead Reckoning
# UPD - Lowlevel memory manipulation
    ("UPD-UPLOAD", 12 + 16) :
        ["<III" + "B"*16, ["StartAddr", "DataSize", "Flags", "B0", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15"]],
    ("UPD-UPLOAD", 12 + 1) :
        ["<III" + "B", ["StartAddr", "DataSize", "Flags", "B0"]],
    ("UPD-DOWNL", 8 + 1) :
        ["<II" + "B", ["StartAddr", "Flags", "B0"]],
    ("UPD-DOWNL", 8) :
        ["<II", ["StartAddr", "Flags"]],
    ("MON-SCHD", 24) :
        ["<IIIIHHHBB", ["TSKRUN", "TSKSCHD", "TSKOVRR", "TSKREG", "STACK", "STACKSIZE", "CPUIDLE", "FLYSLY", "PTLSLY"]],
# MON - GPS system statistics
    ("MON-HW", 60) :
        # ["<IIIIHHBBBxI" + ("B" * 32) + "I" + ("x" * 8), ["PinSel", "PinBank", "PinDir", "PinVal", "NoisePerMS", "AGCCnt", "AStatus", "APower", "flags", "useMask", "v0", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12", "v13", "v14", "v15", "v16", "v17", "v18", "v19", "v20", "v21", "v22", "v23", "v24", "v25", "v26", "v27", "v28", "v29", "v30", "v31", "PinIRQ"]],
        # M8 protocol
        ["<IIIIHHBBBxI" + ("B" * 17) + "BxxIII", ["PinSel", "PinBank", "PinDir", "PinVal", "NoisePerMS", "AGCCnt", "AStatus", "APower", "flags", "useMask", "v0", "v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8", "v9", "v10", "v11", "v12", "v13", "v14", "v15", "v16", "JamInd", "PinIRQ", "PullH", "PullL"]],
    ("MON-VER", None) :
        [40, "<30s10s", ["SWVersion", "HWVersion"], 30, "<30s", ["Extension"]],
    ("MON-IPC", 28) :
        ["<I16sII", ["HNDLRINST", "LASTEVENT", "IRQINST", "IRQCALL"]],
    ("MON-EXCEPT", 316) :
        ["<" + ("I" * 79), ["code", "num", "ur0", "ur1", "ur2", "ur3", "ur4", "ur5", "ur6", "ur7", "ur8", "ur9", "ur10", "ur11", "ur12", "usp", "ulr", "fr8", "fr9", "fr10", "fr11", "fr12", "fsp", "flr", "fspsr", "isp", "ilr", "ispsr", "cpsr", "pc", "us0", "us1", "us2", "us3", "us4", "us5", "us6", "us7", "us8", "us9", "us10", "us11", "us12", "us13", "us14", "us15", "res", "is0", "is1", "is2", "is3", "is4", "is5", "is6", "is7", "is8", "is9", "is10", "is11", "is12", "is13", "is14", "is15", "fs0", "fs1", "fs2", "fs3", "fs4", "fs5", "fs6", "fs7", "fs8", "fs9", "fs10", "fs11", "fs12", "fs13", "fs14", "fs15"]],
    ("AID-INI", 48) :
        ["<iiiIHHIiIIiII", ["X", "Y", "Z", "POSACC", "TM_CFG", "WN", "TOW", "TOW_NS", "TACC_MS", "TACC_NS", "CLKD", "CLKDACC", "FLAGS"]],
    ("AID-DATA", 0) :
        ["", []],
    ("AID-HUI", 72) :
        ["<IddiHHHHHHffffffffI", ["HEALTH", "UTC_A1", "UTC_A0", "UTC_TOT", "UTC_WNT",
         "UTC_LS", "UTC_WNF", "UTC_DN", "UTC_LSF", "UTC_SPARE", "KLOB_A0", "KLOB_A1",
         "KLOB_A2", "KLOB_A3", "KLOB_B0", "KLOB_B1", "KLOB_B2", "KLOB_B3", "FLAGS"]],
    ("AID-ALM", 1) :
        ["<B", ["SVID"]],
    ("AID-ALM", 8)  :
        ["<II", ["SVID", "WEEK"]],
    ("AID-ALM", 40) :
        ["<" + "I"*10, ["SVID", "WEEK", "DWRD0", "DWRD1", "DWRD2", "DWRD3", "DWRD4", "DWRD5", "DWRD6", "DWRD7"]],
    ("AID-EPH", 1) :
        ["<B", ["SVID"]],
    ("AID-EPH", 8) :
        ["<II", ["SVID", "HOW"]],
    ("AID-EPH", 104) :
        ["<" + "I"*26, ["SVID", "HOW", "SF1D0", "SF1D1", "SF1D2", "SF1D3", "SF1D4",
            "SF1D5", "SF1D6", "SF1D7", "SF2D0", "SF2D1", "SF2D2", "SF2D3", "SF2D4",
            "SF2D5", "SF2D6", "SF2D7", "SF3D0", "SF3D1", "SF3D2", "SF3D3", "SF3D4", "SF3D5", "SF3D6", "SF3D7"]],
# TIM - Timekeeping
# ESF - External Sensor Fusion
    ("ESF-STATUS", None) :
        [16, "<IB" + "x"*7 + "BxxB", ["ITOW", "Version", "FusionMode", "NumSens"], 4, "BBBB", ["SensStatus1", "SensStatus2", "Freq", "Faults"]],
    ("ESF-INS", 36) :
        ["<IIIiiiiii", ["Bitfield0", "Reserved", "ITOW", "XAngRate", "YAngRate", "ZAngRate", "XAccel", "YAccel", "ZAccel"]],
    ("ESF-MEAS", None) :
        [8, "<IHH", ["TimeTag", "Flags", "Id"], 4, "<I", ["Data"]],
    ("ESF-RAW", None) :
        [4, "<I", ["Reserved"], 8, "<II", ["Data", "STimeTag"]],  
# HNR - High Rate Navigation
    ("HNR-PVT", 72) :
        ["<IHBBBBBBiBBxxiiiiiiiiIIIIxxxx", ["ITOW", "Year", "Month", "Day", "Hour", "Min", "Sec", "Valid", "Nano", "GPSFix", "Flags", "LON", "LAT", "HEIGHT", "HMSL", "GSpeed", "Speed", "HeadMot", "HeadVeh", "Hacc", "Vacc", "SAcc", "HeadAcc"]],
# MGA - High Rate Navigation
    ("MGA-GPS-EPH", 68) :
        ["<BBBxBBBbHHxbhihhihhIIHhihhiiihxx", ["Type", "Version", "SVID", "FitInterval", "URAIndex", "SvHealth", "TGD", "IODC", "TOC", "AF2", "AF1", "AF0", "CRS", "DeltaN", "M0", "CUC", "CUS", "E", "SqrtA", "TOE", "CIC", "Omega0", "CIS", "CRC", "I0", "Omega", "OmegaDot", "IDot"]],
    ("MGA-GPS-ALM", 36) :
        ["<BBBBHBBhhIiiihhxxxx", ["Type", "Version", "SVID", "SvHealth", "E", "AlmWNa", "TOA", "DeltaI", "OmegaDot", "SqrtA", "Omega0", "Omega", "M0", "AF0", "AF1"]],
    ("MGA-GLO-EPH", 48) :
        ["<BBBxBBBbiiiiiibbbBhBbixxxx", ["Type", "Version", "SVID", "FT", "B", "M", "H", "X", "Y", "Z", "DX", "DY", "DZ", "DDX", "DDY", "DDZ", "TB", "Gamma", "E", "DeltaTau", "Tau"]],
    ("MGA-GLO-ALM", 36) :
        ["<BBBxHBBhHiiIibbhxxxx", ["Type", "Version", "SVID", "N", "M", "C", "Tau", "Epsilon", "Lambda", "DeltaI", "TLambda", "DeltaT", "DeltaDT", "H", "Omega"]],
    ("MGA-INI-TIME_UTC", 24) :
        ["<BBBbHBBBBBxIHxxI", ["Type", "Version", "Ref", "LeapSecs", "Year", "Month", "Day", "Hour", "Minute", "Second", "Ns", "TAccS", "TAccNs"]],
}   

MSGFMT_INV = dict( [ [(CLIDPAIR[clid], le),v + [clid]] for (clid, le),v in MSGFMT.items() ] )

GNSSID = {'GPS': 0,
          'SBAS': 1,
          'Galileo': 2,
          'BeiDou': 3,
          'IMES': 4,
          'QZSS': 5,
          'GLONASS': 6,
         }

GNSSID_INV = dict( [(v,k) for k, v in GNSSID.items()] )

clearMaskShiftDict = {'ioPort':   0,
             'msgConf':  1,
             'infMsg':   2,
             'navConf':  3,
             'rxmConf':  4,
             'rinvConf': 9,
             'antConf':  10,
             'logConf':  11,
             # 'ftsConf':  12
            }

navBbrMaskShiftDict = {'eph':    0,
                       'alm':    1,
                       'health': 2,
                       'klob':   3,
                       'pos':    4,
                       'clkd':   5,
                       'osc':    6,
                       'utc':    7,
                       'rtc':    8,
                       'sfdr':   11,
                       'vmon':   12,
                       'aop':    15,
                      }

resetModeDict = {'hw': 0, 
                 'sw': 1,
                 'swGnssOnly': 2,
                 'hwAfterShutdown': 4, 
                 'gnssStop': 8,
                 'gnssStart': 9
                }

powerSetupValueDict = {'fullPower': 0,
                       'balanced': 1,
                       'interval': 2,
                       'aggressive1Hz': 3,
                       'aggressive2Hz': 4,
                       'aggressive4Hz': 5
                      }

timeRefDict = {'utc': 0,
               'gps': 1,
               'glonass': 2,
               'beidou': 3,
               'galileo': 4
              }

PORTID = {'I2C': 0,
          'UART1': 1,
          'UART2': 2,
          'USB': 3,
          'SPI': 4,
          }

PORTID_INV = dict( [(v,k) for k, v in PORTID.items()] )


class UbloxMessage(object):
    def __init__(self):
        pass

    @staticmethod
    def getMessageFromBuffer(buf, start=0):
        while start < len(buf) - 1:
            index = buf[start:].find(b'\xb5\x62')
            if index >= 0:
                start += index
                result = UbloxMessage.validate(buf[start:])
                if result['valid']:
                    msgClass = result['class']
                    msgId = result['id']
                    length = result['length']
                    rawLength = length + 8
                    rawMessage = buf[start:start+rawLength]
                    start += rawLength

                    return rawMessage, msgClass, msgId, length, start
                else:
                    # Not enough data
                    if not result['lengthMatch']:
                        return None, None, None, None, start
                    # Invalid message, move past sync bytes and continue search
                    elif not result['checksum']:
                        start += 2
            # No sync bytes found, move start to the last byte
            else:
                start = len(buf) - 1

        return None, None, None, None, start

    @staticmethod
    def parse(message):
        message = bytearray(message)

        # Validate message
        result = UbloxMessage.validate(message)
        msgClass = result['class']
        msgId = result['id']
        length = result['length']

        if not result['valid']:
            if not result['sync']:
                raise ValueError('Invalid sync bytes!')
            if not result['lengthMatch']:
                raise ValueError('Message truncated!')
            if not result['checksum']:
                raise ValueError('Checksum invalid!')
            raise ValueError('Invalid message!')

        # Return excess data
        if len(message) > (length + 8):
            remainder = message[length+8:]
            message = message[:length+8]
        else:
            remainder = None

        # Decode UBX message
        try:
            msgFormat, msgData = UbloxMessage.decode(msgClass, msgId, length, message[6:length+6])
        except ValueError:
            return None, None, remainder

        return msgFormat, msgData, remainder

    @staticmethod
    def validate(message):
        result = {'sync': False, 'class': None, 'id': None, 'length': None, 'lengthMatch': False, 'checksum': False, 'valid': False}
        start = 0

        if (message[0] != SYNC1) or (message[1] != SYNC2):
            return result

        result['sync'] = True

        if len(message) < 6:
            return result

        # Decode header - message class, id, and length
        (msgClass, msgId, length) = struct.unpack("<BBH", message[2:6])

        result['class'] = msgClass
        result['id'] = msgId
        result['length'] = length

        # Check that there is enough data in the buffer to match the length
        if len(message) < length + 8:
            result['lengthMatch'] = False
            return result

        result['lengthMatch'] = True

        # Validate checksum
        if UbloxMessage.checksum(message[2:length+6]) != struct.unpack("<BB", message[length+6:length+8]):
            result['checksum'] = False
        else:
            result['checksum'] = True

        result['valid'] = True

        return result

    @staticmethod
    def decode(cl, id, length, payload):
        data = []
        try:
            msgFormat = MSGFMT_INV[((cl, id), length)]
            data.append(dict(zip(msgFormat[1], struct.unpack(msgFormat[0], payload))))
        except KeyError:
            try:
                # Try if this is one of the variable field messages
                msgFormat = MSGFMT_INV[((cl, id), None)]
                fmt_base = msgFormat[:3]
                fmt_rep = msgFormat[3:]
                # Check if the length matches
                if (length - fmt_base[0])%fmt_rep[0] != 0:
                    logging.warning( "Variable length message class 0x%x, id 0x%x \
                        has wrong length %i" % ( cl, id, length ) )
                    raise ValueError( "Variable length message class 0x%x, id 0x%x \
                        has wrong length %i" % ( cl, id, length ) )
                data.append(dict(zip(fmt_base[2], struct.unpack(fmt_base[1], payload[:fmt_base[0]]))))
                for i in range(0, (length - fmt_base[0])//fmt_rep[0]):
                    offset = fmt_base[0] + fmt_rep[0] * i
                    data.append(dict(zip(fmt_rep[2], struct.unpack(fmt_rep[1], payload[offset:offset+fmt_rep[0]]))))

            except KeyError:
                logging.warning( "Don't know how to parse message class 0x%x, id 0x%x, length %i" % ( cl, id, length ) )
                raise ValueError( "Don't know how to parse message class 0x%x, id 0x%x, length %i" % ( cl, id, length ) )

        return msgFormat[-1], data

    @staticmethod
    def buildMessage(clid, length, payload):
        stream = struct.pack("<BBBBH", SYNC1, SYNC2, CLIDPAIR[clid][0], CLIDPAIR[clid][1], length)
        if length > 0:
            try:
                fmt_base = [length] + MSGFMT[(clid,length)]
                fmt_rep = [0, "", []]
                payload_base = payload
            except KeyError:
                format = MSGFMT[(clid, None)]
                fmt_base = format[:3]
                fmt_rep = format[3:]
                payload_base = payload[0]
                payload_rep = payload[1:]
                if (length - fmt_base[0])%fmt_rep[0] != 0:
                    logging.error( "Cannot send: Variable length message class \
                        0x%x, id 0x%x has wrong length %i" % ( cl, id, length ) )
                    return
            stream = stream + struct.pack(fmt_base[1], *[payload_base[i] for i in fmt_base[2]])
            if fmt_rep[0] != 0:
                for i in range(0, (length - fmt_base[0])//fmt_rep[0]):
                    stream = stream + struct.pack(fmt_rep[1], *[payload_rep[i][j] for j in fmt_rep[2]])
        stream = stream + struct.pack("<BB", *UbloxMessage.checksum( stream[2:] ))
        return stream

    @staticmethod
    def decodeNmeaBuffer(buf):
        # This assumes the data buffer is NMEA data and looks for messages
        messages = buf.split('\r\n')

        order = ['sync', 'class', 'id', 'length', 'lengthMatch', 'checksum']

        if len(messages):
            start = messages[0].find('$')
            if start > 0:
                unknown = messages[0][:start]
                messages[0] = messages[0][start:]
                logging.debug('Unknown data ({} bytes): {}'.format(len(unknown), repr(unknown)))
                result = UbloxMessage.validate(unknown)
                logging.debug(', '.join('{}: {}'.format(key, result[key]) for key in order))

        output = []
        for message in messages:
            if len(message) == 0:
                continue

            start = message.find(',')
            
            if message[0] != '$' or start < 0 or not message[1:start].isalpha():
                logging.debug('Unknown data ({} bytes): {}'.format(len(message), repr(message)))
                result = UbloxMessage.validate(message)
                logging.debug(', '.join('{}: {}'.format(key, result[key]) for key in order))
                continue    

            if len(message) < 3 or message[-3] != '*':
                logging.debug('Possible truncated NMEA string: ({} bytes): {}'.format(len(message), repr(message)))
                continue

            output.append(message)
            
        return output

    @staticmethod
    def checksum(msg):
        msg = bytearray(msg)
        ck_a = 0
        ck_b = 0
        for i in msg:
            ck_a = ck_a + i
            ck_b = ck_b + ck_a
        ck_a = ck_a % 256
        ck_b = ck_b % 256
        return (ck_a, ck_b)

    @staticmethod
    def buildMask(enabledBits, shiftDict):
        if enabledBits is None or enabledBits == ['none']:
            return 0
        
        if 'all' in enabledBits:
            enabledBits = shiftDict.keys()

        mask = 0
        for bit in enabledBits:
            if bit not in shiftDict:
                raise Exception('{} is not a valid bit! Must be one of: {}'.format(bit, shiftDict.keys()))
            mask |= (1 << shiftDict[bit])

        return mask

    @staticmethod
    def printMessage(messageType, data, messageTime=None, header=None, fmt='long'):
        if fmt == 'short':
            output = ''
            if messageTime is not None:
                output += '[{}] '.format(datetime.datetime.fromtimestamp(messageTime).strftime('%Y-%m-%d %H:%M:%S.%f'))
            output += messageType
            print(output)
            return

        if header is not None:
            print('\n{}{}:'.format(header, messageType))
        else:    
            print('\n{}:'.format(messageType))

        if messageType == 'CFG-PRT':
            print('    Port ID: {}'.format(data[1]['PortID']))
            print('    TX ready: 0x{:02x}'.format(data[1]['TxReady']))
            if data[1]['PortID'] in [0, 1, 4]:
                print('    Mode: 0x{:04x}'.format(data[1]['Mode']))
            if data[1]['PortID'] == 1:
                print('    Baud rate: {}'.format(data[1]['Baudrate']))
            print('    In proto mask:  0x{:02x}'.format(data[1]['In_proto_mask']))
            print('    Out proto mask: 0x{:02x}'.format(data[1]['Out_proto_mask']))
            if data[1]['PortID'] in [0, 1, 4]:
                print('    Flags: 0x{:02x}'.format(data[1]['Flags']))
        elif messageType == 'MON-VER':
            print('    Software version: {}'.format(data[0]['SWVersion'].decode('ascii').strip()))
            print('    Hardware version: {}'.format(data[0]['HWVersion'].decode('ascii').strip()))
            for i in range(1, len(data)):
                print('    Extension: {}'.format(data[i]['Extension'].decode('ascii').strip()))
        elif messageType == 'NAV-PVT':
            print('    ITOW: {}'.format(data[0]['ITOW']))
            seconds = data[0]['Sec'] + data[0]['Nano']/1e9
            print('    UTC: {:04d}-{:02d}-{:2d} {:02d}:{:02d}:{:012.9f}'.format(data[0]['Year'], data[0]['Month'], data[0]['Day'], data[0]['Hour'], data[0]['Min'], seconds))
            print('        Seconds: {}, Nano: {}'.format(data[0]['Sec'], data[0]['Nano']))
            print('    Valid: 0x{:02x}'.format(data[0]['Valid']))
            print('    Time accuracy: {} ns'.format(data[0]['TAcc']))
            print('    Fix type: {}'.format(data[0]['FixType']))
            print('    Flags:  0x{:02x}'.format(data[0]['Flags']))
            print('    Flags2: 0x{:02x}'.format(data[0]['Flags2']))
            print('    NumSV: {}'.format(data[0]['NumSV']))
            print('    Position: {:.7f}, {:.7f}, {:.3f} m'.format(data[0]['LAT']/1e7, data[0]['LON']/1e7, data[0]['HEIGHT']/1e3))
            print('    HMSL: {:.3f} m'.format(data[0]['HMSL']/1e3))
            print('    PDOP: {:.2f}'.format(data[0]['PDOP']/1e2))
            print('    Horizontal accuracy: {:.3f} m'.format(data[0]['Hacc']/1e3))
            print('    Vertical accuracy:   {:.3f} m'.format(data[0]['Vacc']/1e3))
            print('    Velocity - N: {:.3f}, E: {:.3f}, D: {:.3f} (m/s)'.format(data[0]['VEL_N']/1e3, data[0]['VEL_E']/1e3, data[0]['VEL_D']/1e3))
            print('    Ground speed:   {:.3f} m/s'.format(data[0]['GSpeed']/1e3))
            print('    Speed accuracy: {:.3f} m/s'.format(data[0]['SAcc']/1e3))
            print('    Heading of motion:  {:.5f} deg'.format(data[0]['HeadMot']/1e5))
            print('    Heading of vehicle: {:.5f} deg'.format(data[0]['HeadVeh']/1e5))
            print('    Heading accuracy:   {:.5f} deg'.format(data[0]['HeadAcc']/1e5))
            print('    Magnetic declination: {:.2f} deg'.format(data[0]['MagDec']/1e2))
            print('    Magnetic accuracy:    {:.2f} deg'.format(data[0]['MagAcc']/1e2))

        elif messageType == 'NAV-STATUS':
            print('    ITOW: {}'.format(data[0]['ITOW']))
            print('    GPSFix: {}'.format(data[0]['GPSfix']))
            print('    Flags: 0x{:02x}'.format(data[0]['Flags']))
            print('    TTFF: {:.3f} s'.format(data[0]['TTFF']/1e3))
            print('    MSSS: {:.3f} s'.format(data[0]['MSSS']/1e3))
        else:
            for dataDict in data:
                for field, value in dataDict.items():
                    print('    {}: {}'.format(field, value))
