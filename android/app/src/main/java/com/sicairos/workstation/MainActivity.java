package com.sicairos.workstation;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.browser.customtabs.CustomTabsIntent;

public class MainActivity extends Activity {
    private static final Uri WORKSPACE = Uri.parse("https://209connect.com/members/app.html");
    private TextView message;
    private int dp(int value) { return Math.round(value * getResources().getDisplayMetrics().density); }
    private TextView label(String text, int size, int color) {
        TextView view = new TextView(this);
        view.setText(text); view.setTextSize(size); view.setTextColor(color);
        view.setGravity(Gravity.CENTER); view.setLineSpacing(dp(3), 1f);
        return view;
    }
    private void space(LinearLayout parent, int height) {
        parent.addView(new android.view.View(this), new LinearLayout.LayoutParams(1, dp(height)));
    }
    private void showBuildDetails() {
        new android.app.AlertDialog.Builder(this).setTitle("Build details")
            .setMessage("Version: " + BuildConfig.VERSION_NAME + "\nBuild: " + BuildConfig.VERSION_CODE +
                "\nPackage: " + BuildConfig.APPLICATION_ID + "\n\n" +
                (BuildConfig.DEBUG ? "Debug/test build - not production-signed." :
                    "Release variant - check the build receipt for signing details."))
            .setPositiveButton("Close", null).show();
    }
    private boolean isWorkspaceUrl(Uri uri) {
        if (uri == null || !"https".equals(uri.getScheme()) || uri.getUserInfo() != null ||
            (uri.getPort() != -1 && uri.getPort() != 443)) return false;
        String route = uri.getPath(), prefix = "/david-sicairos-site";
        if ("sicairos4.github.io".equals(uri.getHost())) {
            if (route == null || !route.startsWith(prefix + "/")) return false;
            route = route.substring(prefix.length());
        } else if (!"209connect.com".equals(uri.getHost())) return false;
        return java.util.Arrays.asList("/members/app.html", "/members/workstation.html",
            "/login.html", "/recover.html", "/members/guest.html", "/members/install.html",
            "/android-download.html").contains(route);
    }
    private void openWorkspace() {
        try {
            new CustomTabsIntent.Builder().setShowTitle(true).setUrlBarHidingEnabled(true)
                .setToolbarColor(Color.rgb(27,77,56)).build().launchUrl(this, WORKSPACE);
            message.setText("Your Workstation uses a browser-backed app window. On supported browsers its toolbar can hide as you scroll. Login and saved data use the same website account. This is not a fully native planner.");
        } catch (ActivityNotFoundException error) {
            try { startActivity(new Intent(Intent.ACTION_VIEW, WORKSPACE)); }
            catch (ActivityNotFoundException unavailable) { message.setText("Install or enable a web browser, then choose Enter Workstation."); }
        }
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        final int green=Color.rgb(27,77,56),muted=Color.rgb(77,97,83);
        android.widget.ScrollView scroll=new android.widget.ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackground(new android.graphics.drawable.GradientDrawable(
            android.graphics.drawable.GradientDrawable.Orientation.TL_BR,
            new int[]{Color.rgb(235,244,237),Color.rgb(250,248,240)}));
        if(android.os.Build.VERSION.SDK_INT>=30){
            getWindow().setDecorFitsSystemWindows(false);
            scroll.setOnApplyWindowInsetsListener((view,insets)->{
                android.graphics.Insets safe=insets.getInsets(android.view.WindowInsets.Type.systemBars()|
                    android.view.WindowInsets.Type.displayCutout());
                view.setPadding(safe.left,safe.top,safe.right,safe.bottom);
                return insets;
            });
        }else scroll.setFitsSystemWindows(true);
        LinearLayout page=new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);page.setGravity(Gravity.CENTER);
        page.setPadding(dp(20),dp(28),dp(20),dp(28));
        scroll.addView(page,new android.widget.ScrollView.LayoutParams(-1,-2));
        LinearLayout card=new LinearLayout(this);
        card.setOrientation(LinearLayout.VERTICAL);card.setGravity(Gravity.CENTER_HORIZONTAL);
        card.setPadding(dp(24),dp(28),dp(24),dp(24));
        android.graphics.drawable.GradientDrawable background=new android.graphics.drawable.GradientDrawable();
        background.setColor(Color.WHITE);background.setCornerRadius(dp(24));
        background.setStroke(dp(1),Color.rgb(207,220,207));card.setBackground(background);
        page.addView(card,new LinearLayout.LayoutParams(-1,-2));
        ImageView logo=new ImageView(this);logo.setImageResource(R.drawable.workstation_brand);
        logo.setContentDescription("209 Workstation logo");logo.setScaleType(ImageView.ScaleType.FIT_CENTER);
        card.addView(logo,new LinearLayout.LayoutParams(dp(96),dp(96)));
        space(card,20);
        TextView eyebrow=label("209 Connect",13,muted);card.addView(eyebrow);
        space(card,10);
        TextView title=label("Your Workstation",30,green);
        title.setTypeface(android.graphics.Typeface.DEFAULT,android.graphics.Typeface.BOLD);
        if(android.os.Build.VERSION.SDK_INT>=28)title.setAccessibilityHeading(true);
        card.addView(title);space(card,12);
        message=label("Plan your day, focus on what matters, and reflect.",17,muted);
        message.setAccessibilityLiveRegion(android.view.View.ACCESSIBILITY_LIVE_REGION_POLITE);
        card.addView(message);space(card,26);
        Button open=new Button(this);open.setText("Enter Workstation");open.setAllCaps(false);
        open.setTextSize(17);open.setTextColor(Color.WHITE);
        open.setBackgroundTintList(android.content.res.ColorStateList.valueOf(green));
        open.setMinHeight(dp(52));open.setOnClickListener(view->openWorkspace());
        card.addView(open,new LinearLayout.LayoutParams(-1,-2));space(card,12);
        card.addView(label("Online workspace - internet connection required.",13,muted));
        space(page,20);
        String visibleVersion=BuildConfig.VERSION_NAME.replaceFirst("-(?:debug|fullscreen-test)$","");
        page.addView(label("Version " + visibleVersion,13,muted));
        Button details=new Button(this);details.setText("Build details");details.setAllCaps(false);
        details.setTextColor(green);details.setMinHeight(dp(48));
        details.setOnClickListener(view->showBuildDetails());page.addView(details);
        setContentView(scroll);scroll.requestApplyInsets();
    }
}
