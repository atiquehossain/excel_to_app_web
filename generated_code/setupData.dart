static const String income-lost_ufind_v2 = "income-lost";
static const String loss_of_livelihood_ufind_v2 = "loss_of_livelihood";
static const String loss_of_livelihood_type_ufind_v2 = "loss_of_livelihood_type";
static const String lost_income_6_month_ufind_v2 = "lost_income_6_month";
static const String natural_disasters_affected_ufind_v2 = "natural_disasters_affected";
else if (modelName == SetupConstant.income-lost_ufind_v2) {
  items.add(SetupModel(Languages.getText(context)!.farming_income-lost_ufind_v2, "1"));
}

else if (modelName == SetupConstant.loss_of_livelihood_ufind_v2) {
  items.add(SetupModel(Languages.getText(context)!.yes_loss_of_livelihood_ufind_v2, "1"));
}

else if (modelName == SetupConstant.loss_of_livelihood_type_ufind_v2) {
  items.add(SetupModel(Languages.getText(context)!.agriculture_loss_of_livelihood_type_ufind_v2, "1"));
}

else if (modelName == SetupConstant.lost_income_6_month_ufind_v2) {
  items.add(SetupModel(Languages.getText(context)!.yes_lost_income_6_month_ufind_v2, "1"));
}

else if (modelName == SetupConstant.natural_disasters_affected_ufind_v2) {
  items.add(SetupModel(Languages.getText(context)!.flood_natural_disasters_affected_ufind_v2, "1"));
}

