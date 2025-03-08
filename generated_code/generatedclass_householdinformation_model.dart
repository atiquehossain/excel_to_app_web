import "package:flutter/material.dart";

class GeneratedClass_HouseholdInformation {
  static String definition = "";
  static String more_than_one_family = "";
  static String family_submitted_application = "";
  static String family_data_collected = "";
  static String family_members_count = "";
  static String member_serial_no = "";
  static String family_with_parents_info = "";

  // Constructor
  GeneratedClass_HouseholdInformation();

  // Factory method to create from JSON
  factory GeneratedClass_HouseholdInformation.fromJson(Map<String, dynamic> json) {
    final model = GeneratedClass_HouseholdInformation();
    model.definition = json["definition"] ?? "";
    model.more_than_one_family = json["more_than_one_family"] ?? "";
    model.family_submitted_application = json["family_submitted_application"] ?? "";
    model.family_data_collected = json["family_data_collected"] ?? "";
    model.family_members_count = json["family_members_count"] ?? "";
    model.member_serial_no = json["member_serial_no"] ?? "";
    model.family_with_parents_info = json["family_with_parents_info"] ?? "";
    return model;
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      "definition": definition,
      "more_than_one_family": more_than_one_family,
      "family_submitted_application": family_submitted_application,
      "family_data_collected": family_data_collected,
      "family_members_count": family_members_count,
      "member_serial_no": member_serial_no,
      "family_with_parents_info": family_with_parents_info,
    };
  }
}