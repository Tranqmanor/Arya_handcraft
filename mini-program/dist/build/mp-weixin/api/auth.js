"use strict";const t=require("./request.js");exports.getMe=function(){return t.http.get("/users/me")},exports.loginWithCode=function(e){return t.http.post("/auth/login",{code:e},!1)};
