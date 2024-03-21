"""
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:siac_sms_gateway/models/message.dart';
import 'package:siac_sms_gateway/models/token.dart';
import 'package:siac_sms_gateway/services/refresh_token.dart';
import 'package:siac_sms_gateway/utils/constants.dart';
import 'package:siac_sms_gateway/utils/logger.dart';

Future<void> sendSmsData(Message message,
    {SharedPreferences? prefs, String? refreshToken}) async {
  debugPrint("Sending SMS data");
  final match = regExp.firstMatch(message.body);

  if (match != null) {
    final String phoneNumber = match.namedGroup("phoneNumber")!;
    final String amount = match.namedGroup("amount")!;
    final String date = match.namedGroup("date")!;
    final String hour = match.namedGroup("hour")!;
    final String number = match.namedGroup("number")!;

    Token token;

    try {
      if (refreshToken != null) {
        token = await fetchRefreshToken(refreshToken: refreshToken);
      } else {
        prefs ??= await SharedPreferences.getInstance();
        token = await fetchRefreshToken(preferences: prefs);
      }
    } catch (error) {
      debugPrint(error.toString());
      return;
    }

    final response = await http.post(
      Uri.parse("$host/api/v1/deposits/mobile_payment/from_sms/"),
      headers: token.getHeaders(),
      body: jsonEncode(<String, dynamic>{
        'address': message.address,
        'timestamp': message.date,
        'datetime': "$date $hour",
        'amount': amount,
        'phone_number': phoneNumber,
        'number': number.substring(number.length - 10),
        'subject': message.subject,
        'subscriptionId': message.subscriptionId,
        'serviceCenterAddress': message.serviceCenterAddress,
      }),
    );

    if (!{200, 201, 400, 401}.contains(response.statusCode)) {
      log.severe("Error sending SMS data");
      throw Exception("Error sending SMS data");
    }
  } else {
    log.warning("No match found for message");
  }
}

"""

from urllib.parse import urljoin

import aiohttp

from src.constants import HOST
from src.storages import Storage

