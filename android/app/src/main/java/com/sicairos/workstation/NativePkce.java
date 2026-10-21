package com.sicairos.workstation;
import java.net.URI;
import java.net.URLDecoder;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.SecureRandom;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
public final class NativePkce {
 public static final long TTL_MS=600000L;
 public final String nonce,verifier; public final long created;
 public NativePkce(String nonce,String verifier,long created){if(nonce==null||!nonce.matches("[A-Za-z0-9_-]{43}")||verifier==null||!verifier.matches("[A-Za-z0-9_-]{43}")||created<0)throw new IllegalArgumentException("Invalid attempt");this.nonce=nonce;this.verifier=verifier;this.created=created;}
 private static String random(){byte[] bytes=new byte[32];new SecureRandom().nextBytes(bytes);return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);}
 public static NativePkce create(long now){return new NativePkce(random(),random(),now);}
 public static String challenge(String verifier){try{return Base64.getUrlEncoder().withoutPadding().encodeToString(MessageDigest.getInstance("SHA-256").digest(verifier.getBytes(StandardCharsets.US_ASCII)));}catch(Exception e){throw new IllegalStateException("SHA-256 unavailable");}}
 private static String enc(String value){try{return URLEncoder.encode(value,"UTF-8");}catch(Exception e){throw new IllegalArgumentException("Invalid URL");}}
 public String redirect(String scheme){if(scheme==null||!scheme.matches("[a-z][a-z0-9.]+"))throw new IllegalArgumentException("Invalid scheme");return scheme+"://oauth/callback?attempt="+nonce;}
 public String authorize(String scheme){return "https://uwidjnnhdgtrpsymuhwp.supabase.co/auth/v1/authorize?provider=google&redirect_to="+enc(redirect(scheme))+"&code_challenge="+challenge(verifier)+"&code_challenge_method=s256";}
 public static final class Callback{public final String code;public final boolean denied;private Callback(String code,boolean denied){this.code=code;this.denied=denied;}}
 public Callback callback(String value,String scheme,long now){try{if(now<created||now-created>TTL_MS)throw new IllegalArgumentException();URI uri=new URI(value);if(!scheme.equals(uri.getScheme())||!"oauth".equals(uri.getRawAuthority())||!"/callback".equals(uri.getRawPath())||uri.getRawFragment()!=null||uri.getRawQuery()==null)throw new IllegalArgumentException();Map<String,String> query=new HashMap<>();for(String pair:uri.getRawQuery().split("&",-1)){String[] p=pair.split("=",2);if(p.length!=2)throw new IllegalArgumentException();String key=URLDecoder.decode(p[0],"UTF-8"),item=URLDecoder.decode(p[1],"UTF-8");if(!java.util.Arrays.asList("attempt","code","error","error_code","error_description").contains(key)||query.put(key,item)!=null)throw new IllegalArgumentException();}if(!MessageDigest.isEqual(nonce.getBytes(StandardCharsets.UTF_8),query.getOrDefault("attempt","").getBytes(StandardCharsets.UTF_8)))throw new IllegalArgumentException();boolean denied=query.containsKey("error")||query.containsKey("error_code");if(denied){if(query.containsKey("code"))throw new IllegalArgumentException();return new Callback(null,true);}String code=query.get("code");if(code==null||!code.matches("[A-Za-z0-9._~-]{1,2048}"))throw new IllegalArgumentException();return new Callback(code,false);}catch(Exception e){throw new IllegalArgumentException("Invalid or expired sign-in callback");}}
}
