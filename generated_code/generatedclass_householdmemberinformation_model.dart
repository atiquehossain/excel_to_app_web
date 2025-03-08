import "package:flutter/material.dart";

class GeneratedClass_HouseholdMemberInformation {
  static String relationship = "";
  static String full_name = "";
  static String gender = "";
  static String marital_status = "";
  static String dob = "";
  static String age = "";
  static String mobile_no = "";
  static String id_card_no = "";
  static String id_front_photo = "";
  static String id_back_photo = "";
  static String member_photo = "";
  static String current_education = "";
  static String higher_education = "";
  static String vocational_education
 = "";
  static String nature_of_job = "";
  static String department_of_job = "";
  static String received_walfare_assistance = "";
  static String walfare_type = "";
  static String difficulties = "";
  static String extent_difficulty = "";
  static String member_disability = "";
  static String disability = "";
  static String medical_records = "";
  static String chronic_illness = "";
  static String chronic_disease = "";
  static String kidney_disease = "";
  static String treatment_hospital_name = "";
  static String dialysis = "";
  static String dialysis_report = "";
  static String Member_image = "";
  static String bank_title = "";
  static String account_holder = "";
  static String bank_account_nominee = "";
  static String bank_name = "";
  static String bank_branch = "";
  static String acc_number_passbook = "";
  static String account_number = "";
  static String account_type = "";
  static String ownership = "";

  // Constructor
  GeneratedClass_HouseholdMemberInformation();

  // Factory method to create from JSON
  factory GeneratedClass_HouseholdMemberInformation.fromJson(Map<String, dynamic> json) {
    final model = GeneratedClass_HouseholdMemberInformation();
    model.relationship = json["relationship"] ?? "";
    model.full_name = json["full_name"] ?? "";
    model.gender = json["gender"] ?? "";
    model.marital_status = json["marital_status"] ?? "";
    model.dob = json["dob"] ?? "";
    model.age = json["age"] ?? "";
    model.mobile_no = json["mobile_no"] ?? "";
    model.id_card_no = json["id_card_no"] ?? "";
    model.id_front_photo = json["id_front_photo"] ?? "";
    model.id_back_photo = json["id_back_photo"] ?? "";
    model.member_photo = json["member_photo"] ?? "";
    model.current_education = json["current_education"] ?? "";
    model.higher_education = json["higher_education"] ?? "";
    model.vocational_education
 = json["vocational_education
"] ?? "";
    model.nature_of_job = json["nature_of_job"] ?? "";
    model.department_of_job = json["department_of_job"] ?? "";
    model.received_walfare_assistance = json["received_walfare_assistance"] ?? "";
    model.walfare_type = json["walfare_type"] ?? "";
    model.difficulties = json["difficulties"] ?? "";
    model.extent_difficulty = json["extent_difficulty"] ?? "";
    model.member_disability = json["member_disability"] ?? "";
    model.disability = json["disability"] ?? "";
    model.medical_records = json["medical_records"] ?? "";
    model.chronic_illness = json["chronic_illness"] ?? "";
    model.chronic_disease = json["chronic_disease"] ?? "";
    model.kidney_disease = json["kidney_disease"] ?? "";
    model.treatment_hospital_name = json["treatment_hospital_name"] ?? "";
    model.dialysis = json["dialysis"] ?? "";
    model.dialysis_report = json["dialysis_report"] ?? "";
    model.Member_image = json["Member_image"] ?? "";
    model.bank_title = json["bank_title"] ?? "";
    model.account_holder = json["account_holder"] ?? "";
    model.bank_account_nominee = json["bank_account_nominee"] ?? "";
    model.bank_name = json["bank_name"] ?? "";
    model.bank_branch = json["bank_branch"] ?? "";
    model.acc_number_passbook = json["acc_number_passbook"] ?? "";
    model.account_number = json["account_number"] ?? "";
    model.account_type = json["account_type"] ?? "";
    model.ownership = json["ownership"] ?? "";
    return model;
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      "relationship": relationship,
      "full_name": full_name,
      "gender": gender,
      "marital_status": marital_status,
      "dob": dob,
      "age": age,
      "mobile_no": mobile_no,
      "id_card_no": id_card_no,
      "id_front_photo": id_front_photo,
      "id_back_photo": id_back_photo,
      "member_photo": member_photo,
      "current_education": current_education,
      "higher_education": higher_education,
      "vocational_education
": vocational_education
,
      "nature_of_job": nature_of_job,
      "department_of_job": department_of_job,
      "received_walfare_assistance": received_walfare_assistance,
      "walfare_type": walfare_type,
      "difficulties": difficulties,
      "extent_difficulty": extent_difficulty,
      "member_disability": member_disability,
      "disability": disability,
      "medical_records": medical_records,
      "chronic_illness": chronic_illness,
      "chronic_disease": chronic_disease,
      "kidney_disease": kidney_disease,
      "treatment_hospital_name": treatment_hospital_name,
      "dialysis": dialysis,
      "dialysis_report": dialysis_report,
      "Member_image": Member_image,
      "bank_title": bank_title,
      "account_holder": account_holder,
      "bank_account_nominee": bank_account_nominee,
      "bank_name": bank_name,
      "bank_branch": bank_branch,
      "acc_number_passbook": acc_number_passbook,
      "account_number": account_number,
      "account_type": account_type,
      "ownership": ownership,
    };
  }
}