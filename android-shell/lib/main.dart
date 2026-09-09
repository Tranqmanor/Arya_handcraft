import 'dart:convert';
import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:webview_flutter_android/webview_flutter_android.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  // 状态栏文字用深色(页面顶栏为浅色背景)
  SystemChrome.setSystemUIOverlayStyle(
    const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.dark,
      statusBarBrightness: Brightness.light,
    ),
  );
  runApp(const AryaAdminApp());
}

class AryaAdminApp extends StatelessWidget {
  const AryaAdminApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Arya手作 管理',
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFFA98B84),
        useMaterial3: true,
      ),
      home: const WebShellPage(),
    );
  }
}

class WebShellPage extends StatefulWidget {
  const WebShellPage({super.key});

  @override
  State<WebShellPage> createState() => _WebShellPageState();
}

class _WebShellPageState extends State<WebShellPage> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFFFAF6F0))
      // CSV 导出原生桥:JS 侧 window.exportCsv.postMessage("<文件名>\u0000<内容>")
      ..addJavaScriptChannel('exportCsv', onMessageReceived: _onExportCsv)
      // 文件选择原生桥:JS 侧 window.filePicker.postMessage('{"reqId":..,"kind":"image|csv"}')
      ..addJavaScriptChannel('filePicker', onMessageReceived: _onPickFile)
      ..setNavigationDelegate(
        NavigationDelegate(
          onWebResourceError: (e) {
            if (kDebugMode && e.isForMainFrame != false) {
              debugPrint('web error: ${e.description}');
            }
          },
        ),
      )
      ..loadFlutterAsset('webapp/index.html');

    final platform = _controller.platform;
    if (platform is AndroidWebViewController) {
      // 允许 WebView 内 video 自动/手动播放策略放宽
      platform.setMediaPlaybackRequiresUserGesture(false);
    }
    // 注:setWebContentsDebuggingEnabled 需 webview_flutter>=4.10,4.8.0 无此 API,
    // 如需 Chrome 远程调试请升级依赖后再启用。
  }

  /// 原生文件选择(经 SAF 系统选择器,无需存储权限),结果以 base64 dataURL 回传 H5。
  Future<void> _onPickFile(JavaScriptMessage msg) async {
    String reqId = '';
    try {
      final req = jsonDecode(msg.message) as Map<String, dynamic>;
      reqId = (req['reqId'] ?? '') as String;
      final kind = (req['kind'] ?? 'image') as String;

      final result = kind == 'csv'
          ? await FilePicker.platform.pickFiles(
              type: FileType.custom,
              allowedExtensions: ['csv', 'txt'],
              withData: true,
            )
          : await FilePicker.platform.pickFiles(
              type: FileType.image,
              withData: true,
            );

      final file = (result?.files.isNotEmpty ?? false) ? result!.files.first : null;
      if (file == null || file.bytes == null) {
        // 用户取消
        await _replyPick(reqId, null, null, null);
        return;
      }
      final mime = kind == 'csv' ? 'text/csv' : (file.extension == 'png' ? 'image/png' : 'image/jpeg');
      await _replyPick(reqId, file.name, base64Encode(file.bytes!), mime);
    } catch (e) {
      if (kDebugMode) debugPrint('pick failed: $e');
      await _replyPick(reqId, null, null, null);
    }
  }

  Future<void> _replyPick(String reqId, String? name, String? data, String? mime) async {
    if (reqId.isEmpty) return;
    final payload = jsonEncode({'reqId': reqId, 'name': name, 'data': data, 'mime': mime});
    await _controller
        .runJavaScript('window.__onNativeFile && window.__onNativeFile($payload)');
  }

  Future<void> _onExportCsv(JavaScriptMessage msg) async {
    final i = msg.message.indexOf('\u0000');
    if (i < 0) return;
    final name = msg.message.substring(0, i);
    final data = msg.message.substring(i + 1);
    try {
      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/$name');
      await file.writeAsString(data);
      await Share.shareXFiles([XFile(file.path)], subject: name);
    } catch (e) {
      if (kDebugMode) debugPrint('export failed: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFFAF6F0),
      // 让出系统状态栏与手势条区域,避免遮挡页面顶栏/底部 TabBar
      body: SafeArea(
        top: true,
        bottom: true,
        child: WebViewWidget(controller: _controller),
      ),
    );
  }
}
