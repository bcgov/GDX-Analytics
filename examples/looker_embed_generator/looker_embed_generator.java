/**
 *Class          : looker_embed_generator.java
 *
 *Description    : Sample Java class to generate secure Looker
 *               : embed codes that include custom filters.
 * 
 *Requirements   : You must set the following environment variable
 *               : to establish credentials for the embed user:
 * 
 *               : export LOOKERKEY=<<Looker embed key>> ## bash
 *               : set LOOKERKEY=<<Looker embed key>>    :: cmd
 *               : $env:LOOKERKEY = "testing"            ## powershell 
 * 
 *Usage          : java looker_embed_generator.class <<embed url>>
 *               :
 *               : eg: java looker_embed_generator.class dashboards/18 dev
 *               :
 *               : NOTE: The embed must be accessible to the 
 *               : Embed Shared Group.
 *               :
 *References     : https://github.com/looker/looker_embed_sso_examples/
 *               : https://docs.looker.com/reference/embedding/sso-embed#building_the_embed_url
 *               : https://docs.looker.com/reference/embedding/embed-javascript-events
 * 
*/

import java.math.BigInteger;
import java.security.SecureRandom;
import java.util.Calendar;
import java.util.Date;
import java.util.Map;
import java.util.Base64;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

public class looker_embed_generator {

    public static void main(String [] args){

        String lookerURL = "52.60.65.121:9999";  // looker host as address:port
        String lookerKey = ""; // LOOKERKEY environment variable (see Requirements)
        String externalUserID = "50";  // converted to JSON string
        String firstName = "\"Dashboard\""; // converted to JSON string
        String lastName = "\"User\""; // converted to JSON string
        String permissions = "[\"see_lookml_dashboards\",+\"access_data\",+\"see_user_dashboards\",+\"see_looks\"]"; // converted to JSON array
        String models = "[\"all\"]"; // converted to JSON array
        String groupIDs = "[]"; // converted to JSON array, can be set to null (value, not JSON) for no groups
        String externalGroupID = "\"external_group_id\"";  // converted to JSON string
        String sessionLength = "900";
        String embedURL = "";
        String forceLogoutLogin = "true"; // converted to JSON bool
        String accessFilters = ("{}");  // converted to JSON Object of Objects
        String userAttributes = "{\"can_see_sensitive_data\": \"YES\"}";  // A Map<String, String> converted to JSON object

        if (args.length != 1) {
            System.err.println("Usage: java looker_embed_generator.class <<embed url>>");
            System.exit(1);
        }

        embedURL = "/embed/" + args[0] + "?embed_domain=http://127.0.0.1:5000";

        lookerKey = System.getenv("LOOKERKEY");
        if (lookerKey == null) {
            System.err.println("Environment variable LOOKERKEY doesn't exist");
            System.exit(1);
        }

        try {

            String url = createURL(lookerURL, lookerKey, externalUserID, firstName, lastName, permissions, models,
                                   sessionLength, accessFilters, embedURL, forceLogoutLogin, groupIDs,
                                   externalGroupID, userAttributes);
            System.out.println("https://" + url);

        } catch(Exception e){
            System.out.println(e);
        }
    }

    /**TODO: builder pattern */
    public static String createURL(String lookerURL, String lookerKey,
                                   String userID, String firstName, String lastName, String userPermissions,
                                   String userModels, String sessionLength, String accessFilters,
                                   String embedURL, String forceLogoutLogin, String groupIDs,
                                   String externalGroupID, String userAttributes) throws Exception {

        String path = "/login/embed/" + java.net.URLEncoder.encode(embedURL, "UTF-8");



        Calendar cal = Calendar.getInstance();
        SecureRandom random = new SecureRandom();
        String nonce = "\"" + (new BigInteger(130, random).toString(32)) + "\"";  // converted to JSON string
        String time = Long.toString(cal.getTimeInMillis() / 1000L);

        // Order of these here is very important!
        String urlToSign = "";
        urlToSign += lookerURL + "\n";
        urlToSign += path + "\n";
        urlToSign += nonce + "\n";
        urlToSign += time + "\n";
        urlToSign += sessionLength + "\n";
        urlToSign += userID + "\n";
        urlToSign += userPermissions + "\n";
        urlToSign += userModels + "\n";
        urlToSign += groupIDs + "\n";
        urlToSign += externalGroupID + "\n";
        urlToSign += userAttributes + "\n";
        urlToSign += accessFilters;

        String signature =  encodeString(urlToSign, lookerKey);

        // you need to %20-encode each parameter before you add to the URL
        String signedURL = "nonce="    + java.net.URLEncoder.encode(nonce, "UTF-8") +
                "&time="               + java.net.URLEncoder.encode(time, "UTF-8") +
                "&session_length="     + java.net.URLEncoder.encode(sessionLength, "UTF-8") +
                "&external_user_id="   + java.net.URLEncoder.encode(userID, "UTF-8") +
                "&permissions="        + java.net.URLEncoder.encode(userPermissions, "UTF-8") +
                "&models="             + java.net.URLEncoder.encode(userModels, "UTF-8") +
                "&access_filters="     + java.net.URLEncoder.encode(accessFilters, "UTF-8") +
                "&signature="          + java.net.URLEncoder.encode(signature, "UTF-8") +
                "&first_name="         + java.net.URLEncoder.encode(firstName, "UTF-8") +
                "&last_name="          + java.net.URLEncoder.encode(lastName, "UTF-8") +
                "&group_ids="          + java.net.URLEncoder.encode(groupIDs, "UTF-8") +
                "&external_group_id="  + java.net.URLEncoder.encode(externalGroupID, "UTF-8") +
                "&user_attributes="    + java.net.URLEncoder.encode(userAttributes, "UTF-8") +
                "&force_logout_login=" + java.net.URLEncoder.encode(forceLogoutLogin, "UTF-8");

        return lookerURL + path + '?' + signedURL;

    }

    public static String encodeString(String stringToEncode, String lookerKey) throws Exception {
        byte[] keyBytes = lookerKey.getBytes();
        SecretKeySpec signingKey = new SecretKeySpec(keyBytes, "HmacSHA1");
        Mac mac = Mac.getInstance("HmacSHA1");
        mac.init(signingKey);
        byte[] rawHmac = Base64.getEncoder().encode(mac.doFinal(stringToEncode.getBytes("UTF-8")));
        return new String(rawHmac, "UTF-8");
    }
}
