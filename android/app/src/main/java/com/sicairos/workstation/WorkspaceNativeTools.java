package com.sicairos.workstation;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.function.Supplier;
import org.json.JSONTokener;

/** User-selected documents and text-only report printing; no broad storage permission. */
public final class WorkspaceNativeTools extends WebChromeClient {
    public static final int PICK_DOCUMENT = 210;
    private final Activity activity;
    private final Supplier<WebView> source;
    private ValueCallback<Uri[]> chooser;
    private String chooserContext;
    private boolean multiple, closed;
    private int generation;
    private WebView reportView;
    public WorkspaceNativeTools(Activity activity, Supplier<WebView> source){this.activity=activity;this.source=source;}
    private boolean allowed(WebView view){
        if(closed||activity.isFinishing()||activity.isDestroyed()||view==null||view!=source.get()||view.getParent()==null||view.getUrl()==null)return false;
        Uri u=Uri.parse(view.getUrl());
        return "https".equals(u.getScheme())&&"209connect.com".equals(u.getHost())&&u.getUserInfo()==null&&(u.getPort()==-1||u.getPort()==443)&&("/members/app.html".equals(u.getPath())||"/members/guest.html".equals(u.getPath()));
    }
    private void message(String text){if(!closed&&!activity.isFinishing())Toast.makeText(activity,text,Toast.LENGTH_LONG).show();}
    private void context(WebView view,ValueCallback<String> done){
        if(!allowed(view)){done.onReceiveValue(null);return;}
        view.evaluateJavascript("(function(){var a=window.WorkstationApp,s=document.documentElement.dataset.memberState||'';if(a&&a.busy)return null;if(location.pathname==='/members/app.html'&&(!a||!['ready','demo'].includes(s)))return null;return JSON.stringify([location.href,a?String(a.context):'guest',a?String(a.day):'',s]);})()",value->{
            done.onReceiveValue(allowed(view)&&value!=null&&value.startsWith("\"")?value:null);
        });
    }
    private void finishChooser(Uri[] values){ValueCallback<Uri[]> old=chooser;chooser=null;chooserContext=null;generation++;if(old!=null)old.onReceiveValue(values);}
    public void cancelChooser(){finishChooser(null);}
    @Override public boolean onShowFileChooser(WebView view,ValueCallback<Uri[]> callback,FileChooserParams params){
        cancelChooser();
        if(!allowed(view)||params==null){callback.onReceiveValue(null);return true;}
        chooser=callback;multiple=params.getMode()==FileChooserParams.MODE_OPEN_MULTIPLE;final int token=generation;
        String[] accept=params.getAcceptTypes();ArrayList<String> types=new ArrayList<>();
        if(accept!=null)for(String item:accept){if(item==null)continue;for(String part:item.split(",")){String type=part.trim();if(type.matches("[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+*-]+"))types.add(type);else if(".json".equalsIgnoreCase(type))types.add("application/json");else if(".pdf".equalsIgnoreCase(type))types.add("application/pdf");}}
        context(view,value->{
            if(token!=generation||chooser!=callback)return;
            if(value==null){cancelChooser();message("Load the current day before choosing a file.");return;}
            chooserContext=value;
            Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);intent.addCategory(Intent.CATEGORY_OPENABLE);intent.setType(types.size()==1?types.get(0):"*/*");
            if(types.size()>1)intent.putExtra(Intent.EXTRA_MIME_TYPES,types.toArray(new String[0]));intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE,multiple);intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            try{activity.startActivityForResult(intent,PICK_DOCUMENT);}catch(Exception error){cancelChooser();message("No document picker is available. No file was imported.");}
        });return true;
    }
    public void receive(int result,Intent data){
        if(chooser==null)return;
        if(result!=Activity.RESULT_OK||data==null){cancelChooser();return;}
        LinkedHashSet<Uri> selected=new LinkedHashSet<>();
        if(data.getClipData()!=null){int count=data.getClipData().getItemCount();if(count>5){cancelChooser();message("Choose at most five files.");return;}for(int i=0;i<count;i++)selected.add(data.getClipData().getItemAt(i).getUri());}
        else if(data.getData()!=null)selected.add(data.getData());
        if(selected.isEmpty()||(!multiple&&selected.size()!=1)){cancelChooser();return;}
        for(Uri uri:selected)if(uri==null||!"content".equals(uri.getScheme())){cancelChooser();message("Choose a document from the system picker.");return;}
        final int token=generation;final String expected=chooserContext;final WebView view=source.get();
        context(view,current->{if(token!=generation||chooser==null)return;if(expected==null||!expected.equals(current)){cancelChooser();message("Account or day changed. Choose the file again.");return;}finishChooser(selected.toArray(new Uri[0]));});
    }
    public void markNative(WebView view){if(allowed(view))view.evaluateJavascript("window.__workstationNativePrint=true",null);}
    public void printPreview(){
        final WebView view=source.get();context(view,expected->{if(expected==null){message("Load a day and open its print preview first.");return;}
            view.evaluateJavascript("(function(){var p=document.getElementById('workstationPrintPreview');if(!p)return null;var c=p.cloneNode(true);c.querySelectorAll('script,iframe,object,embed,img,link,.print-actions,button').forEach(function(n){n.remove();});return c.outerHTML;})()",encoded->{
                final String html;try{Object value=new JSONTokener(encoded).nextValue();if(!(value instanceof String)||((String)value).length()>1000000)throw new IllegalArgumentException();html=(String)value;}catch(Exception error){message("Open a supported report preview before printing.");return;}
                if(!allowed(view))return;
                new AlertDialog.Builder(activity).setTitle("Print or save this report?").setMessage("This sends the displayed report snapshot to your chosen printer or PDF destination. Keep private copies secure. Printing does not save planner changes.").setNegativeButton("Cancel",null).setPositiveButton("Continue",(d,w)->context(view,current->{
                    if(!expected.equals(current)){message("Account or day changed. Reopen the report.");return;}
                    if(reportView!=null)reportView.destroy();reportView=new WebView(activity);reportView.getSettings().setJavaScriptEnabled(false);reportView.getSettings().setAllowFileAccess(false);reportView.getSettings().setAllowContentAccess(false);reportView.getSettings().setBlockNetworkLoads(true);
                    reportView.setWebViewClient(new WebViewClient(){private boolean printed;@Override public void onPageFinished(WebView printable,String url){if(printed||closed||activity.isFinishing())return;printed=true;android.print.PrintManager manager=(android.print.PrintManager)activity.getSystemService(Activity.PRINT_SERVICE);if(manager!=null)try{manager.print("209 saved report",printable.createPrintDocumentAdapter("209 saved report"),new android.print.PrintAttributes.Builder().build());}catch(Exception error){message("The print dialog could not open. No PDF save was confirmed.");}}});
                    String style="<style>body{font:12pt/1.5 sans-serif;color:#000;background:#fff}article{break-after:page}article:last-child{break-after:auto}h1,h2,h3{break-after:avoid}p,li{white-space:pre-wrap;overflow-wrap:anywhere}.print-actions,button{display:none}#workstationPrintPreview{position:static;overflow:visible}@page{margin:15mm}</style>";
                    reportView.loadDataWithBaseURL(null,"<!doctype html><html><head><meta charset='utf-8'>"+style+"</head><body>"+html+"</body></html>","text/html","UTF-8",null);
                })).show();
            });
        });
    }
    public void close(){closed=true;cancelChooser();if(reportView!=null){reportView.destroy();reportView=null;}}
}
