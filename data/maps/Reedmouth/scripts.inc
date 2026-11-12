Reedmouth_MapScripts::
	.byte 0

Reedmouth_EventScript_Sign1::
	msgbox Reedmouth_EventScript_Sign1_Text, MSGBOX_SIGN
	end

Reedmouth_EventScript_Sign1_Text:
	.string "REEDMOUTH POKéMON GYM LEADER:\n"
	.string "SEDGE Rooted in the delta!$"

Reedmouth_EventScript_Sign2::
	msgbox Reedmouth_EventScript_Sign2_Text, MSGBOX_SIGN
	end

Reedmouth_EventScript_Sign2_Text:
	.string "UNDERPASS Under the LETHYS to\n"
	.string "VALECROWN CITY$"

Reedmouth_EventScript_Sign3::
	msgbox Reedmouth_EventScript_Sign3_Text, MSGBOX_SIGN
	end

Reedmouth_EventScript_Sign3_Text:
	.string "REEDMOUTH The river ends, the sea\n"
	.string "begins.$"

Reedmouth_EventScript_Npc1::
	msgbox Reedmouth_EventScript_Npc1_Text, MSGBOX_NPC
	end

Reedmouth_EventScript_Npc1_Text:
	.string "The harbour ferry runs up the\n"
	.string "LETHYS when the water is high\p"
	.string "enough. These days it hardly ever\n"
	.string "is.$"

Reedmouth_EventScript_Npc2::
	msgbox Reedmouth_EventScript_Npc2_Text, MSGBOX_NPC
	end

Reedmouth_EventScript_Npc2_Text:
	.string "Fresh water meets salt water right\n"
	.string "here. You can catch all sorts!$"

Reedmouth_EventScript_Npc3::
	msgbox Reedmouth_EventScript_Npc3_Text, MSGBOX_NPC
	end

Reedmouth_EventScript_Npc3_Text:
	.string "SEDGE says the reeds clean the\n"
	.string "river before it reaches the sea.$"

Reedmouth_EventScript_Npc4::
	msgbox Reedmouth_EventScript_Npc4_Text, MSGBOX_NPC
	end

Reedmouth_EventScript_Npc4_Text:
	.string "Seel!$"

Reedmouth_EventScript_Item5::
	finditem ITEM_MYSTIC_WATER
	end

Reedmouth_EventScript_Npc6::
	msgbox Reedmouth_EventScript_Npc6_Text, MSGBOX_NPC
	end

Reedmouth_EventScript_Npc6_Text:
	.string "I have fished here for sixty\n"
	.string "years. The biggest one always gets\p"
	.string "away.$"
