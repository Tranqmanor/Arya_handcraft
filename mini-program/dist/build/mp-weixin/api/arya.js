"use strict";const s=require("./request.js");exports.clearSessions=function(){return s.http.post("/arya/sessions",{})},exports.sendMessage=function(e){return s.http.post("/arya/chat",{message:e})};
