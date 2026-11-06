Reedmouth_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, Reedmouth_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

Reedmouth_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_REEDMOUTH
	end

Reedmouth_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_REEDMOUTH_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end
