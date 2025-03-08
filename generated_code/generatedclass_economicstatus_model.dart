import "package:flutter/material.dart";

class GeneratedClass_EconomicStatus {
  static String samurdhi_benefit = "";
  static String samurdhi_amount = "";
  static String samurdhi_account = "";
  static String samurdhi_zone = "";
  static String have_land = "";
  static String total_cultivable_land = "";
  static String crops_grown_land = "";
  static String have_cultivable_paddy_land = "";
  static String total_cultivable_paddy_land = "";
  static String have_owns_vehicles = "";
  static String vehicles_type = "";
  static String have_economic_machinery = "";
  static String machinery_type = "";
  static String  machinary _image = "";
  static String have_animal_husbandry_livestock = "";
  static String animal_husbandry_livestock_type = "";
  static String monthly_expenses = "";
  static String monthly_income = "";
  static String electricity_consumer = "";
  static String electricity_unit = "";
  static String electricity_account_number = "";
  static String house_type = "";
  static String house_floor_type = "";
  static String house_roof_type = "";
  static String house_wall_type = "";
  static String house_floor_area = "";
  static String has_secure_door_windows = "";
  static String residential_nature = "";
  static String residential_ownership = "";
  static String has_other_house = "";
  static String light_source = "";
  static String drinking_water_source = "";
  static String sanitation_facilities = "";
  static String toilet_type = "";
  static String latitude = "";
  static String longitude = "";
  static String photo_of_house = "";
  static String required_fuel_type = "";
  static String  monthly_fuel_amount = "";
  static String cooking_fuel_type = "";

  // Constructor
  GeneratedClass_EconomicStatus();

  // Factory method to create from JSON
  factory GeneratedClass_EconomicStatus.fromJson(Map<String, dynamic> json) {
    final model = GeneratedClass_EconomicStatus();
    model.samurdhi_benefit = json["samurdhi_benefit"] ?? "";
    model.samurdhi_amount = json["samurdhi_amount"] ?? "";
    model.samurdhi_account = json["samurdhi_account"] ?? "";
    model.samurdhi_zone = json["samurdhi_zone"] ?? "";
    model.have_land = json["have_land"] ?? "";
    model.total_cultivable_land = json["total_cultivable_land"] ?? "";
    model.crops_grown_land = json["crops_grown_land"] ?? "";
    model.have_cultivable_paddy_land = json["have_cultivable_paddy_land"] ?? "";
    model.total_cultivable_paddy_land = json["total_cultivable_paddy_land"] ?? "";
    model.have_owns_vehicles = json["have_owns_vehicles"] ?? "";
    model.vehicles_type = json["vehicles_type"] ?? "";
    model.have_economic_machinery = json["have_economic_machinery"] ?? "";
    model.machinery_type = json["machinery_type"] ?? "";
    model. machinary _image = json[" machinary _image"] ?? "";
    model.have_animal_husbandry_livestock = json["have_animal_husbandry_livestock"] ?? "";
    model.animal_husbandry_livestock_type = json["animal_husbandry_livestock_type"] ?? "";
    model.monthly_expenses = json["monthly_expenses"] ?? "";
    model.monthly_income = json["monthly_income"] ?? "";
    model.electricity_consumer = json["electricity_consumer"] ?? "";
    model.electricity_unit = json["electricity_unit"] ?? "";
    model.electricity_account_number = json["electricity_account_number"] ?? "";
    model.house_type = json["house_type"] ?? "";
    model.house_floor_type = json["house_floor_type"] ?? "";
    model.house_roof_type = json["house_roof_type"] ?? "";
    model.house_wall_type = json["house_wall_type"] ?? "";
    model.house_floor_area = json["house_floor_area"] ?? "";
    model.has_secure_door_windows = json["has_secure_door_windows"] ?? "";
    model.residential_nature = json["residential_nature"] ?? "";
    model.residential_ownership = json["residential_ownership"] ?? "";
    model.has_other_house = json["has_other_house"] ?? "";
    model.light_source = json["light_source"] ?? "";
    model.drinking_water_source = json["drinking_water_source"] ?? "";
    model.sanitation_facilities = json["sanitation_facilities"] ?? "";
    model.toilet_type = json["toilet_type"] ?? "";
    model.latitude = json["latitude"] ?? "";
    model.longitude = json["longitude"] ?? "";
    model.photo_of_house = json["photo_of_house"] ?? "";
    model.required_fuel_type = json["required_fuel_type"] ?? "";
    model. monthly_fuel_amount = json[" monthly_fuel_amount"] ?? "";
    model.cooking_fuel_type = json["cooking_fuel_type"] ?? "";
    return model;
  }

  // Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      "samurdhi_benefit": samurdhi_benefit,
      "samurdhi_amount": samurdhi_amount,
      "samurdhi_account": samurdhi_account,
      "samurdhi_zone": samurdhi_zone,
      "have_land": have_land,
      "total_cultivable_land": total_cultivable_land,
      "crops_grown_land": crops_grown_land,
      "have_cultivable_paddy_land": have_cultivable_paddy_land,
      "total_cultivable_paddy_land": total_cultivable_paddy_land,
      "have_owns_vehicles": have_owns_vehicles,
      "vehicles_type": vehicles_type,
      "have_economic_machinery": have_economic_machinery,
      "machinery_type": machinery_type,
      " machinary _image":  machinary _image,
      "have_animal_husbandry_livestock": have_animal_husbandry_livestock,
      "animal_husbandry_livestock_type": animal_husbandry_livestock_type,
      "monthly_expenses": monthly_expenses,
      "monthly_income": monthly_income,
      "electricity_consumer": electricity_consumer,
      "electricity_unit": electricity_unit,
      "electricity_account_number": electricity_account_number,
      "house_type": house_type,
      "house_floor_type": house_floor_type,
      "house_roof_type": house_roof_type,
      "house_wall_type": house_wall_type,
      "house_floor_area": house_floor_area,
      "has_secure_door_windows": has_secure_door_windows,
      "residential_nature": residential_nature,
      "residential_ownership": residential_ownership,
      "has_other_house": has_other_house,
      "light_source": light_source,
      "drinking_water_source": drinking_water_source,
      "sanitation_facilities": sanitation_facilities,
      "toilet_type": toilet_type,
      "latitude": latitude,
      "longitude": longitude,
      "photo_of_house": photo_of_house,
      "required_fuel_type": required_fuel_type,
      " monthly_fuel_amount":  monthly_fuel_amount,
      "cooking_fuel_type": cooking_fuel_type,
    };
  }
}