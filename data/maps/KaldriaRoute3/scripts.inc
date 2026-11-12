KaldriaRoute3_MapScripts::
	.byte 0

KaldriaRoute3_EventScript_Sign1::
	msgbox KaldriaRoute3_EventScript_Sign1_Text, MSGBOX_SIGN
	end

KaldriaRoute3_EventScript_Sign1_Text:
	.string "LOWBANK RUINS A village that stood\n"
	.string "here before the dam.$"

KaldriaRoute3_EventScript_Npc1::
	msgbox KaldriaRoute3_EventScript_Npc1_Text, MSGBOX_NPC
	end

KaldriaRoute3_EventScript_Npc1_Text:
	.string "These walls are older than the\n"
	.string "dam, older than STILLBROOK even.\p"
	.string "Who built them?$"

KaldriaRoute3_EventScript_Npc2::
	msgbox KaldriaRoute3_EventScript_Npc2_Text, MSGBOX_NPC
	end

KaldriaRoute3_EventScript_Npc2_Text:
	.string "People say the old village of\n"
	.string "LOWBANK is still down there, under\p"
	.string "the lake.$"

KaldriaRoute3_EventScript_Item3::
	finditem ITEM_REVIVE
	end

KaldriaRoute3_EventScript_Npc4::
	msgbox KaldriaRoute3_EventScript_Npc4_Text, MSGBOX_NPC
	end

KaldriaRoute3_EventScript_Npc4_Text:
	.string "I found an old coin in these ruins\n"
	.string "once! Maybe there's more if you\p"
	.string "look really carefully.$"

KaldriaRoute3_EventScript_Npc5::
	msgbox KaldriaRoute3_EventScript_Npc5_Text, MSGBOX_NPC
	end

KaldriaRoute3_EventScript_Npc5_Text:
	.string "This was the inn of LOWBANK.\n"
	.string "Travellers rested here before\p"
	.string "crossing the river.$"
