import "package:flutter/material.dart";

class GeneratedClass_HouseholdMemberInformation {
  final String switch;
  final String switch_in_sinhala;
  final String switch_in_tamil;
  final String no_of_questions;
  final String labels_in_english;
  final String database;
  final String labels_in_sinhala;
  final String labels_in_tamil;
  final String questions_in_english;
  final String questions_in_sinhala;
  final String questions_in_tamil;
  final String mandatorynot_mandatory;
  final String data_type;
  final String skip_logics;
  final String field_names_in_english;
  final String field_names_in_sinhala;
  final String field_names_in_tamil;

  GeneratedClass_HouseholdMemberInformation({
    required this.switch,
    required this.switch_in_sinhala,
    required this.switch_in_tamil,
    required this.no_of_questions,
    required this.labels_in_english,
    required this.database,
    required this.labels_in_sinhala,
    required this.labels_in_tamil,
    required this.questions_in_english,
    required this.questions_in_sinhala,
    required this.questions_in_tamil,
    required this.mandatorynot_mandatory,
    required this.data_type,
    required this.skip_logics,
    required this.field_names_in_english,
    required this.field_names_in_sinhala,
    required this.field_names_in_tamil,
  }});

  factory GeneratedClass_HouseholdMemberInformation.fromJson(Map<String, dynamic> json) {
    return GeneratedClass_HouseholdMemberInformation(
      switch: json["switch"] as String,
      switch_in_sinhala: json["switch_in_sinhala"] as String,
      switch_in_tamil: json["switch_in_tamil"] as String,
      no_of_questions: json["no_of_questions"] as String,
      labels_in_english: json["labels_in_english"] as String,
      database: json["database"] as String,
      labels_in_sinhala: json["labels_in_sinhala"] as String,
      labels_in_tamil: json["labels_in_tamil"] as String,
      questions_in_english: json["questions_in_english"] as String,
      questions_in_sinhala: json["questions_in_sinhala"] as String,
      questions_in_tamil: json["questions_in_tamil"] as String,
      mandatorynot_mandatory: json["mandatorynot_mandatory"] as String,
      data_type: json["data_type"] as String,
      skip_logics: json["skip_logics"] as String,
      field_names_in_english: json["field_names_in_english"] as String,
      field_names_in_sinhala: json["field_names_in_sinhala"] as String,
      field_names_in_tamil: json["field_names_in_tamil"] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      "switch": switch,
      "switch_in_sinhala": switch_in_sinhala,
      "switch_in_tamil": switch_in_tamil,
      "no_of_questions": no_of_questions,
      "labels_in_english": labels_in_english,
      "database": database,
      "labels_in_sinhala": labels_in_sinhala,
      "labels_in_tamil": labels_in_tamil,
      "questions_in_english": questions_in_english,
      "questions_in_sinhala": questions_in_sinhala,
      "questions_in_tamil": questions_in_tamil,
      "mandatorynot_mandatory": mandatorynot_mandatory,
      "data_type": data_type,
      "skip_logics": skip_logics,
      "field_names_in_english": field_names_in_english,
      "field_names_in_sinhala": field_names_in_sinhala,
      "field_names_in_tamil": field_names_in_tamil,
    };
  }
}