import "package:flutter/material.dart";

class GeneratedClass {
  static String natural_disasters_affected = "";
  static String latitude = "";
  static String longitude = "";
  static String lost_income_6_month = "";
  static String income-lost = "";
  static String loss_of_livelihood = "";
  static String loss_of_livelihood_type = "";

  // Constructor
  GeneratedClass();

  // Factory method to create from JSON
  factory GeneratedClass.fromJson(Map<String, dynamic> json) {
    final model = GeneratedClass();
    model.natural_disasters_affected = json["natural_disasters_affected"] ?? "";
    model.latitude = json["latitude"] ?? "";
    model.longitude = json["longitude"] ?? "";
    model.lost_income_6_month = json["lost_income_6_month"] ?? "";
    model.income-lost = json["income-lost"] ?? "";
    model.loss_of_livelihood = json["loss_of_livelihood"] ?? "";
    model.loss_of_livelihood_type = json["loss_of_livelihood_type"] ?? "";
    return model;
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      "natural_disasters_affected": natural_disasters_affected,
      "latitude": latitude,
      "longitude": longitude,
      "lost_income_6_month": lost_income_6_month,
      "income-lost": income-lost,
      "loss_of_livelihood": loss_of_livelihood,
      "loss_of_livelihood_type": loss_of_livelihood_type,
    };
  }
}