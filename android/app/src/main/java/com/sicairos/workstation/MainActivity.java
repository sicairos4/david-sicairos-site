package com.sicairos.workstation;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import androidx.browser.customtabs.CustomTabsIntent;

public class MainActivity extends Activity {
    private static final Uri WORKSPACE = Uri.parse("https://sicairos4.github.io/david-sicairos-site/members/workstation.html");
    private TextView message;
    private void openWorkspace() {
        try {
            new CustomTabsIntent.Builder().setShowTitle(true).setUrlBarHidingEnabled(false)
                .setToolbarColor(Color.rgb(27,77,56)).build().launchUrl(this, WORKSPACE);
            message.setText("Your Workstation opens in a browser-backed app window. Login and saved data use the same website account. Close that window to return here.");
        } catch (ActivityNotFoundException error) {
            try { startActivity(new Intent(Intent.ACTION_VIEW, WORKSPACE)); }
            catch (ActivityNotFoundException unavailable) { message.setText("Install or enable a web browser, then choose Open my Workstation."); }
        }
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setGravity(Gravity.CENTER);
        int padding = (int)(24 * getResources().getDisplayMetrics().density);
        layout.setPadding(padding,padding,padding,padding);
        layout.setBackgroundColor(Color.rgb(245,248,243));
        TextView title = new TextView(this);
        title.setText("209 Workstation");title.setTextSize(30);title.setTextColor(Color.rgb(27,77,56));
        message = new TextView(this);message.setTextSize(17);message.setPadding(0,padding,0,padding);
        message.setText("Your day, your work, your next useful step.");
        Button open = new Button(this);open.setText("Open my Workstation");open.setOnClickListener(view -> openWorkspace());
        layout.addView(title);layout.addView(message);layout.addView(open);setContentView(layout);
        if(state==null)openWorkspace();
    }
}
