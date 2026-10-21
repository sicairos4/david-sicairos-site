package com.sicairos.workstation;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.webkit.*;
import android.widget.*;

public class MainActivity extends Activity {
    private WebView workspace, printView;
    private String pendingText;
    private int dp(int value){return Math.round(value*getResources().getDisplayMetrics().density);}
    private boolean internal(Uri uri){return uri!=null && "https".equals(uri.getScheme()) && "209connect.com".equals(uri.getHost()) && uri.getUserInfo()==null && (uri.getPort()==-1||uri.getPort()==443) && java.util.Arrays.asList("/members/app.html","/members/guest.html","/login.html","/recover.html","/workspace-start.html","/members/install.html","/android-download.html").contains(uri.getPath());}
    private TextView text(String value,int size,int color){TextView t=new TextView(this);t.setText(value);t.setTextSize(size);t.setTextColor(color);t.setPadding(0,dp(8),0,dp(8));return t;}
    private void welcome(){
        boolean dark=(getResources().getConfiguration().uiMode & 48)==32;
        int bg=dark?Color.rgb(18,23,21):Color.rgb(242,246,238),ink=dark?Color.rgb(243,241,231):Color.rgb(24,62,48);
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(bg);scroll.setFitsSystemWindows(true);
        LinearLayout page=new LinearLayout(this);page.setOrientation(LinearLayout.VERTICAL);page.setGravity(Gravity.CENTER_VERTICAL);page.setPadding(dp(24),dp(28),dp(24),dp(28));scroll.addView(page);
        ImageView logo=new ImageView(this);logo.setImageResource(R.drawable.workstation_brand);logo.setContentDescription("209.");page.addView(logo,new LinearLayout.LayoutParams(dp(76),dp(76)));
        page.addView(text("209 Connect",15,ink));page.addView(text("Make room for your day.",30,ink));page.addView(text("Start with a small morning routine. Make a plan, focus on one thing, and keep a private journal.",17,ink));
        Button enter=new Button(this);enter.setText("Open my workspace");enter.setAllCaps(false);enter.setMinHeight(dp(52));enter.setOnClickListener(v->openPage("https://209connect.com/members/app.html"));page.addView(enter);
        Button help=new Button(this);help.setText("Get started / learn more");help.setAllCaps(false);help.setOnClickListener(v->openPage("https://209connect.com/workspace-start.html"));page.addView(help);
        Button guest=new Button(this);guest.setText("Try the guest planner");guest.setAllCaps(false);guest.setOnClickListener(v->openPage("https://209connect.com/members/guest.html"));page.addView(guest);
        page.addView(text("Online workspace. Save day keeps account edits. Print or export when you want your own copy. Guest work is not saved to an account automatically.",14,ink));
        Button info=new Button(this);info.setText("App information");info.setAllCaps(false);info.setOnClickListener(v->new AlertDialog.Builder(this).setTitle("App information").setMessage("Version: "+BuildConfig.VERSION_NAME+"\nBuild: "+BuildConfig.VERSION_CODE+"\nPackage: "+BuildConfig.APPLICATION_ID+"\n"+(BuildConfig.DEBUG?"Debug preview; not production signed.":"Release variant; consult its signing receipt.")+"\nGoogle return-to-app is not implemented. Email/password and guest mode stay inside this workspace.").setPositiveButton("Close",null).show());page.addView(info);setContentView(scroll);
    }
    private void external(Uri uri){if(uri==null||!"https".equals(uri.getScheme())||uri.getUserInfo()!=null)return;new AlertDialog.Builder(this).setTitle("Open a separate browser?").setMessage("External pages open separately. Google sign-in in the browser does not sign in this embedded preview. Use email/password here until native Google return is implemented.").setPositiveButton("Open browser",(d,w)->{try{startActivity(new Intent(Intent.ACTION_VIEW,uri));}catch(Exception e){Toast.makeText(this,"No browser available",Toast.LENGTH_LONG).show();}}).setNegativeButton("Stay here",null).show();}
    private void openPage(String url){
        if(!internal(Uri.parse(url)))return;
        if(workspace==null){workspace=new WebView(this);WebSettings s=workspace.getSettings();s.setJavaScriptEnabled(true);s.setDomStorageEnabled(true);s.setAllowFileAccess(false);s.setAllowContentAccess(false);s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);CookieManager.getInstance().setAcceptThirdPartyCookies(workspace,false);workspace.setWebChromeClient(new WebChromeClient());workspace.addJavascriptInterface(new Output(),"WorkstationAndroid");
            workspace.setWebViewClient(new WebViewClient(){@Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request){if(internal(request.getUrl()))return false;if(request.isForMainFrame())external(request.getUrl());return true;}@Override public void onReceivedError(WebView view,WebResourceRequest request,WebResourceError error){if(request.isForMainFrame()&&!isFinishing())new AlertDialog.Builder(MainActivity.this).setTitle("Workspace could not load").setMessage("Check your connection. No offline save is promised.").setPositiveButton("Retry",(d,w)->view.reload()).setNegativeButton("Close",null).show();}});
            getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
            if(android.os.Build.VERSION.SDK_INT>=30){getWindow().setDecorFitsSystemWindows(false);workspace.setOnApplyWindowInsetsListener((v,insets)->{android.graphics.Insets safe=insets.getInsets(android.view.WindowInsets.Type.systemBars()|android.view.WindowInsets.Type.displayCutout()|android.view.WindowInsets.Type.ime());v.setPadding(safe.left,safe.top,safe.right,safe.bottom);return insets;});}else workspace.setFitsSystemWindows(true);
        }
        setContentView(workspace);workspace.requestApplyInsets();workspace.loadUrl(url);
    }
    private class Output {
        @JavascriptInterface public void printHtml(String html){if(html==null||html.length()>1000000)return;runOnUiThread(()->{if(workspace==null||!internal(Uri.parse(workspace.getUrl())))return;new AlertDialog.Builder(MainActivity.this).setTitle("Print or save a private copy?").setMessage("The selected content will be sent to your chosen print or PDF destination. Keep private copies secure.").setPositiveButton("Continue",(d,w)->{if(printView!=null)printView.destroy();printView=new WebView(MainActivity.this);printView.getSettings().setJavaScriptEnabled(false);printView.setWebViewClient(new WebViewClient(){@Override public void onPageFinished(WebView view,String url){android.print.PrintManager manager=(android.print.PrintManager)getSystemService(PRINT_SERVICE);if(manager!=null)manager.print("209 private copy",view.createPrintDocumentAdapter("209 private copy"),new android.print.PrintAttributes.Builder().build());}});printView.loadDataWithBaseURL(null,html,"text/html","UTF-8",null);}).setNegativeButton("Cancel",null).show();});}
        @JavascriptInterface public void saveText(String name,String value){if(value==null||value.length()>1000000)return;runOnUiThread(()->{if(workspace==null||!internal(Uri.parse(workspace.getUrl()))||pendingText!=null)return;pendingText=value;Intent i=new Intent(Intent.ACTION_CREATE_DOCUMENT);i.addCategory(Intent.CATEGORY_OPENABLE);i.setType("text/plain");i.putExtra(Intent.EXTRA_TITLE,name!=null&&name.matches("[A-Za-z0-9._-]{1,100}")?name:"209-journal.txt");try{startActivityForResult(i,209);}catch(Exception e){pendingText=null;Toast.makeText(MainActivity.this,"No document destination available",Toast.LENGTH_LONG).show();}});}
    }
    @Override protected void onActivityResult(int request,int result,Intent data){super.onActivityResult(request,result,data);if(request!=209)return;String value=pendingText;pendingText=null;if(result==RESULT_OK&&data!=null&&data.getData()!=null&&value!=null){try(java.io.OutputStream stream=getContentResolver().openOutputStream(data.getData())){if(stream==null)throw new java.io.IOException();stream.write(value.getBytes(java.nio.charset.StandardCharsets.UTF_8));Toast.makeText(this,"Copy saved",Toast.LENGTH_SHORT).show();}catch(Exception e){Toast.makeText(this,"Could not save the copy. Your workspace is unchanged.",Toast.LENGTH_LONG).show();}}}
    @Override public void onCreate(Bundle state){super.onCreate(state);if(android.os.Build.VERSION.SDK_INT>=33)getOnBackInvokedDispatcher().registerOnBackInvokedCallback(android.window.OnBackInvokedDispatcher.PRIORITY_DEFAULT,this::onBackPressed);welcome();}
    @Override public void onBackPressed(){if(workspace!=null&&workspace.getParent()!=null){if(workspace.canGoBack()){workspace.goBack();return;}new AlertDialog.Builder(this).setTitle("Return to welcome?").setMessage("Save or export your day before leaving.").setPositiveButton("Return",(d,w)->welcome()).setNegativeButton("Stay",null).show();}else finish();}
    @Override protected void onPause(){if(workspace!=null)workspace.onPause();super.onPause();}
    @Override protected void onResume(){super.onResume();if(workspace!=null)workspace.onResume();}
    @Override protected void onDestroy(){pendingText=null;if(workspace!=null){workspace.removeJavascriptInterface("WorkstationAndroid");workspace.destroy();}if(printView!=null)printView.destroy();super.onDestroy();}
}
