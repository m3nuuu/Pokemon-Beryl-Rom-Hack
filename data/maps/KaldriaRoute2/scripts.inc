KaldriaRoute2_MapScripts::
	.byte 0

KaldriaRoute2_EventScript_Sign1::
	msgbox KaldriaRoute2_EventScript_Sign1_Text, MSGBOX_SIGN
	end

KaldriaRoute2_EventScript_Sign1_Text:
	.string "ROUTE 2 Up: LETHYS DAM West:\n"
	.string "STILLBROOK$"

KaldriaRoute2_EventScript_Npc1::
	msgbox KaldriaRoute2_EventScript_Npc1_Text, MSGBOX_NPC
	end

KaldriaRoute2_EventScript_Npc1_Text:
	.string "From up here you can hear the dam\n"
	.string "humming. All that water, held back\p"
	.string "by one wall!$"

KaldriaRoute2_EventScript_Npc2::
	msgbox KaldriaRoute2_EventScript_Npc2_Text, MSGBOX_NPC
	end

KaldriaRoute2_EventScript_Npc2_Text:
	.string "These steps were cut when they\n"
	.string "built the dam. My legs hate them.$"
