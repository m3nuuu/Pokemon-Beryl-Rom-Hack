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
