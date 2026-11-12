KaldriaRoute4_MapScripts::
	.byte 0

KaldriaRoute4_EventScript_Sign1::
	msgbox KaldriaRoute4_EventScript_Sign1_Text, MSGBOX_SIGN
	end

KaldriaRoute4_EventScript_Sign1_Text:
	.string "LETHYS POWER STATION$"

KaldriaRoute4_EventScript_Sign2::
	msgbox KaldriaRoute4_EventScript_Sign2_Text, MSGBOX_SIGN
	end

KaldriaRoute4_EventScript_Sign2_Text:
	.string "ROUTE 4 South: VALECROWN CITY$"

KaldriaRoute4_EventScript_Npc1::
	msgbox KaldriaRoute4_EventScript_Npc1_Text, MSGBOX_NPC
	end

KaldriaRoute4_EventScript_Npc1_Text:
	.string "Careful, it's a long drop! You can\n"
	.string "jump down, but there's no way back\p"
	.string "up here.$"

KaldriaRoute4_EventScript_Item2::
	finditem ITEM_HP_UP
	end

KaldriaRoute4_EventScript_Npc3::
	msgbox KaldriaRoute4_EventScript_Npc3_Text, MSGBOX_NPC
	end

KaldriaRoute4_EventScript_Npc3_Text:
	.string "People say the hills behind the\n"
	.string "city hide a cave. I haven't found\p"
	.string "it yet.$"
