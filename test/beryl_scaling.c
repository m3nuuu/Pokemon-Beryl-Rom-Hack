#include "global.h"
#include "event_data.h"
#include "pokemon.h"
#include "beryl_scaling.h"
#include "test/test.h"
#include "constants/opponents.h"

static void MakeLeaderParty(struct Pokemon *party)
{
    static const u8 levels[PARTY_SIZE] = {47, 47, 48, 48, 49, 50};
    u32 i;
    for (i = 0; i < PARTY_SIZE - 1; i++)
        CreateMon(&party[i], SPECIES_GEODUDE, levels[i], 0, OTID_STRUCT_PLAYER_ID);
    CreateMon(&party[PARTY_SIZE - 1], SPECIES_LARVITAR, 50, 0, OTID_STRUCT_PLAYER_ID);
}

TEST("Beryl: a leader brings two Pokemon at the first gym")
{
    struct Pokemon party[PARTY_SIZE];
    u32 i;
    for (i = FLAG_BADGE01_GET; i <= FLAG_BADGE08_GET; i++)
        FlagClear(i);
    MakeLeaderParty(party);
    Beryl_ScaleTrainerParty(party, TRAINER_ROXANNE_1);
    EXPECT_EQ(GetMonData(&party[0], MON_DATA_LEVEL), 9);
    EXPECT_EQ(GetMonData(&party[1], MON_DATA_LEVEL), 12);
    EXPECT_EQ(GetMonData(&party[1], MON_DATA_SPECIES), SPECIES_LARVITAR);
    EXPECT_EQ(GetMonData(&party[2], MON_DATA_SPECIES), SPECIES_NONE);
}

TEST("Beryl: with seven badges a leader brings five evolved Pokemon")
{
    struct Pokemon party[PARTY_SIZE];
    u32 i;
    for (i = FLAG_BADGE01_GET; i <= FLAG_BADGE08_GET; i++)
        FlagClear(i);
    for (i = 0; i < 7; i++)
        FlagSet(FLAG_BADGE01_GET + i);
    MakeLeaderParty(party);
    Beryl_ScaleTrainerParty(party, TRAINER_BRAWLY_1);
    EXPECT_EQ(GetMonData(&party[4], MON_DATA_LEVEL), 54);
    EXPECT_EQ(GetMonData(&party[4], MON_DATA_SPECIES), SPECIES_PUPITAR);
    EXPECT_EQ(GetMonData(&party[0], MON_DATA_SPECIES), SPECIES_GRAVELER);
    EXPECT_EQ(GetMonData(&party[5], MON_DATA_SPECIES), SPECIES_NONE);
    EXPECT_EQ(GetMonData(&party[4], MON_DATA_HP), GetMonData(&party[4], MON_DATA_MAX_HP));
}

TEST("Beryl: other trainers are not scaled")
{
    struct Pokemon party[PARTY_SIZE];
    MakeLeaderParty(party);
    Beryl_ScaleTrainerParty(party, TRAINER_SIDNEY);
    EXPECT_EQ(GetMonData(&party[5], MON_DATA_LEVEL), 50);
}
