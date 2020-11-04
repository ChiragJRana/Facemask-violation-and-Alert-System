package com.example.alarmswitch;

import android.net.UrlQuerySanitizer;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import androidx.appcompat.app.AppCompatActivity;


import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.RequestBody;

public class MainActivity extends AppCompatActivity {

    private Boolean ALARM_STATUS=true;
    private String url = "http://" + "10.0.2.2" + ":" + 5000 + "/";
    private String postBodyString;
    private MediaType mediaType;
    private RequestBody requestBody;
    private Button alarm;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        alarm = findViewById(R.id.alarm_control);
//        String postBodyText = "{'status': 1}";
//        MediaType mediaType = MediaType.parse("text/plain; charset=utf-8");
//        RequestBody postBody = RequestBody.create(mediaType, postBodyText);
        alarm.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                postRequest("{status: 1}", url);
            }

        });

//        alarm.setOnClickListener(new View.OnClickListener() {
//            @Override
//            public void onClick(View v) {
//                    RequestQueue requestQueue = Volley.newRequestQueue(MainActivity.this);
//                    String url = "http://192.168.137.1:3000/test";
//                    //Put your local IPv4 address in here along with the port number
//                    // and replace test with the route in which you want to post the json variable
//                    /*
//                    *   { turn: "false" }  is the json variable sent to the server
//                    * */
//                    Log.d("TAG", "onClick: button clicked ");
//                    StringRequest stringRequest = new StringRequest(Request.Method.POST, url, new Response.Listener<String>() {
//                        @Override
//                        public void onResponse(String response) {
//                            Log.d("TAG", "onResponse: "+response);
//                        }
//                    }, new Response.ErrorListener() {
//                        @Override
//                        public void onErrorResponse(VolleyError error) {
//                            Log.d("TAG", "onErrorResponse:  response"+error);
//                        }
//                    }){
//                        @Override
//                        protected Map<String, String> getParams()  {
//                            Map<String,String> params = new HashMap();
//                            params.put("turn", ALARM_STATUS+"");
//                            return params;
//                        }
//
//                        @Override
//                        public Map<String, String> getHeaders()  {
//                            Map<String,String> params=new HashMap();
//                            params.put("Content-Type","application/x-www-form-urlencoded");
//                            return params;
//                        }
//                    };
//                    requestQueue.add(stringRequest);
//
//                }
//
//        });
    }
    private RequestBody buildRequestBody(String msg) {
        postBodyString = msg;
        mediaType = MediaType.parse("application/json; charset=utf-8");
        requestBody = RequestBody.create(postBodyString, mediaType);
        return requestBody;
    }

    private void postRequest(String postBody, String postUrl ) {

            OkHttpClient client = new OkHttpClient();
            RequestBody requestBody = buildRequestBody(postBody);
            Request request = new Request.Builder()
//                    .header("Content-Type","application/json")
                    .post(requestBody)
                    .url(postUrl)
                    .build();

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(final Call call, final IOException e) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {

                            Log.d("TAG", url);
                            Toast.makeText(MainActivity.this, "Something went wrong:" + " " + e.getMessage(), Toast.LENGTH_LONG).show();
                            call.cancel();


                        }
                    });

                }

                @Override
                public void onResponse(Call call, final Response response) throws IOException {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            try {
                                Toast.makeText(MainActivity.this, response.body().string(), Toast.LENGTH_LONG).show();
//                                Log.d("TAG", )
                            } catch (IOException e) {
//                                e.printStackTrace();
                                Log.d("Tag", e.toString());
                            }
                        }
                    });


                }
            });
        }





}


