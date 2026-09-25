import { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("comment2dm_token");
}

function getAuthHeaders() {
  const token = getToken();

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

function App() {
  const [keyword, setKeyword] = useState("LINK");

  const [productUrl, setProductUrl] = useState("");

  const [dmMessage, setDmMessage] = useState(
    "Here is the link you requested:\n"
  );

  const [campaigns, setCampaigns] = useState([]);

  const [instagram, setInstagram] = useState(null);

  const [loading, setLoading] = useState(false);

  const [authMode, setAuthMode] = useState("login");

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [authLoading, setAuthLoading] = useState(false);

  const [authMessage, setAuthMessage] = useState("");

  const [user, setUser] = useState(null);


  // ========================================================
  // LOAD CAMPAIGNS
  // ========================================================

  async function loadCampaigns() {

    const token = getToken();

    if (!token) {
      setCampaigns([]);
      return;
    }

    try {

      const response = await fetch(
        `${API}/api/campaigns`,
        {
          headers: getAuthHeaders(),
        }
      );

      const data = await response.json();

      setCampaigns(
        data.campaigns || []
      );

    } catch (error) {

      console.error(
        "Campaign loading failed:",
        error
      );

    }
  }


  // ========================================================
  // LOAD INSTAGRAM ACCOUNT
  // ========================================================

  async function loadInstagramAccount() {

    const token = getToken();

    if (!token) {
      setInstagram(null);
      return;
    }

    try {

      const response = await fetch(
        `${API}/api/instagram/accounts`,
        {
          headers: getAuthHeaders(),
        }
      );

      const data = await response.json();

      const accounts = data.accounts || [];
      setInstagram(accounts[0] || null);

    } catch (error) {

      console.error(
        "Instagram account loading failed:",
        error
      );

    }
  }


  // ========================================================
  // INITIAL LOAD
  // ========================================================

  useEffect(() => {

    const savedUser = localStorage.getItem("comment2dm_user");

    if (savedUser) {
      setUser({ email: savedUser });
    }

    loadCampaigns();

    loadInstagramAccount();

  }, []);


  // ========================================================
  // CONNECT INSTAGRAM
  // ========================================================

  async function handleAuthSubmit(event) {
    event.preventDefault();

    if (!email.trim() || !password.trim()) {
      setAuthMessage("Please enter both email and password.");
      return;
    }

    setAuthLoading(true);
    setAuthMessage("");

    try {
      const endpoint = authMode === "login" ? "/api/auth/login" : "/api/auth/register";
      const response = await fetch(`${API}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email: email.trim(), password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || "Authentication failed.");
      }

      localStorage.setItem("comment2dm_token", data.token);
      localStorage.setItem("comment2dm_user", data.user.email);
      setUser(data.user);
      setEmail("");
      setPassword("");
      setAuthMessage("");
      await loadCampaigns();
      await loadInstagramAccount();
    } catch (error) {
      setAuthMessage(error.message);
    } finally {
      setAuthLoading(false);
    }
  }

  function logoutUser() {
    localStorage.removeItem("comment2dm_token");
    localStorage.removeItem("comment2dm_user");
    setUser(null);
    setInstagram(null);
    setCampaigns([]);
    setAuthMessage("You are logged out.");
  }

  function connectInstagram() {

    const token = getToken();

    if (!token) {
      setAuthMode("login");
      setAuthMessage("Please log in to Comment2DM before connecting Instagram.");
      return;
    }

    const url = `${API}/auth/instagram?session=${encodeURIComponent(token)}`;
    window.location.href = url;

  }


  // ========================================================
  // CREATE CAMPAIGN
  // ========================================================

  async function createCampaign() {

    if (!keyword.trim()) {

      alert(
        "Please enter a keyword."
      );

      return;
    }


    if (!productUrl.trim()) {

      alert(
        "Please enter a product URL."
      );

      return;
    }


    setLoading(true);


    const message =
      dmMessage.trim()
        ? `${dmMessage.trim()}\n${productUrl.trim()}`
        : productUrl.trim();


    try {

      const response = await fetch(
        `${API}/api/campaigns`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            ...getAuthHeaders(),
          },

          body: JSON.stringify({
            keyword:
              keyword.trim(),

            product_url:
              productUrl.trim(),

            dm_message:
              message,
          }),
        }
      );


      const data =
        await response.json();


      if (!response.ok) {

        alert(
          data.error ||
          "Could not create campaign."
        );

        return;
      }


      alert(
        data.message
      );


      setProductUrl("");

      setDmMessage(
        "Here is the link you requested:"
      );


      await loadCampaigns();


    } catch (error) {

      alert(
        "Backend is not running."
      );

    } finally {

      setLoading(false);

    }
  }


  // ========================================================
  // DELETE CAMPAIGN
  // ========================================================

  async function deleteCampaign(
    campaignId
  ) {

    const confirmed =
      window.confirm(
        "Delete this campaign?"
      );


    if (!confirmed) {
      return;
    }


    try {

      await fetch(
        `${API}/api/campaigns/${campaignId}`,
        {
          method: "DELETE",
          headers: getAuthHeaders(),
        }
      );

      loadCampaigns();

    } catch (error) {

      alert(
        "Could not delete campaign."
      );

    }
  }


  // ========================================================
  // UI
  // ========================================================

  return (

    <div style={styles.page}>

      <div style={styles.container}>

        <h1 style={styles.title}>
          Comment2DM
        </h1>

        <p style={styles.subtitle}>
          Instagram Comment → DM Automation
        </p>


        {/* ==================================================
            INSTAGRAM CONNECTION
        ================================================== */}

        {!user ? (
          <div style={styles.card}>
            <h2>Login to Comment2DM</h2>
            <p>Sign in or create an account before connecting Instagram.</p>

            <div style={styles.authToggleRow}>
              <button
                type="button"
                style={{
                  ...styles.authToggle,
                  ...(authMode === "login" ? styles.authToggleActive : {}),
                }}
                onClick={() => setAuthMode("login")}
              >
                Login
              </button>
              <button
                type="button"
                style={{
                  ...styles.authToggle,
                  ...(authMode === "register" ? styles.authToggleActive : {}),
                }}
                onClick={() => setAuthMode("register")}
              >
                Register
              </button>
            </div>

            <form onSubmit={handleAuthSubmit}>
              <label style={styles.label}>Email</label>
              <input
                style={styles.input}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                type="email"
              />

              <label style={styles.label}>Password</label>
              <input
                style={styles.input}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                type="password"
              />

              {authMessage ? <p style={styles.authMessage}>{authMessage}</p> : null}

              <button style={styles.button} type="submit" disabled={authLoading}>
                {authLoading ? "Please wait..." : authMode === "login" ? "Login" : "Create account"}
              </button>
            </form>
          </div>
        ) : (
          <div style={styles.card}>
            <h2>Account</h2>
            <p>Logged in as <strong>{user.email}</strong></p>
            <button style={styles.button} onClick={logoutUser}>Logout</button>
          </div>
        )}

        <div style={styles.card}>

          <h2>
            Instagram
          </h2>


          {instagram ? (

            <div>

              <p>
                Connected as{" "}
                <strong>
                  @{instagram.username}
                </strong>
              </p>

              <span style={styles.connected}>
                ● Connected
              </span>

            </div>

          ) : (

            <div>

              <p>
                Connect your Instagram
                Professional account.
              </p>

              <button
                style={styles.instagramButton}
                onClick={connectInstagram}
                disabled={!user}
              >
                {user ? "Connect Instagram" : "Login required"}
              </button>

            </div>

          )}

        </div>


        {/* ==================================================
            CREATE CAMPAIGN
        ================================================== */}

        <div style={styles.card}>

          <h2>
            Create Campaign
          </h2>


          <label style={styles.label}>
            Comment Keyword
          </label>


          <input
            style={styles.input}
            value={keyword}
            onChange={(e) =>
              setKeyword(e.target.value)
            }
            placeholder="LINK"
          />


          <label style={styles.label}>
            Product URL
          </label>


          <input
            style={styles.input}
            value={productUrl}
            onChange={(e) =>
              setProductUrl(e.target.value)
            }
            placeholder="https://example.com/product"
          />


          <label style={styles.label}>
            DM Message
          </label>


          <textarea
            style={styles.textarea}
            value={dmMessage}
            onChange={(e) =>
              setDmMessage(e.target.value)
            }
            placeholder="Here is the link you requested:"
          />


          <button
            style={styles.button}
            onClick={createCampaign}
            disabled={loading}
          >

            {loading
              ? "Creating..."
              : "Create Campaign"}

          </button>

        </div>


        {/* ==================================================
            CAMPAIGNS
        ================================================== */}

        <div style={styles.card}>

          <h2>
            Campaigns
          </h2>


          {campaigns.length === 0 ? (

            <p>
              No campaigns yet.
            </p>

          ) : (

            campaigns.map(
              (campaign) => (

                <div
                  key={campaign.id}
                  style={styles.campaign}
                >

                  <div>

                    <strong>
                      Keyword:
                    </strong>{" "}

                    {campaign.keyword}

                  </div>


                  <div>

                    <strong>
                      Product:
                    </strong>{" "}

                    <a
                      href={
                        campaign.product_url
                      }
                      target="_blank"
                      rel="noreferrer"
                    >
                      {campaign.product_url}
                    </a>

                  </div>


                  <div>

                    <strong>
                      Message:
                    </strong>

                    <p>
                      {campaign.dm_message}
                    </p>

                  </div>


                  <button
                    style={styles.deleteButton}
                    onClick={() =>
                      deleteCampaign(
                        campaign.id
                      )
                    }
                  >
                    Delete
                  </button>

                </div>

              )
            )

          )}

        </div>

      </div>

    </div>

  );
}


// ==========================================================
// STYLES
// ==========================================================

const styles = {

  page: {
    minHeight: "100vh",
    background: "#f5f7fb",
    padding: "40px 20px",
    fontFamily:
      "Arial, sans-serif",
  },


  container: {
    maxWidth: "760px",
    margin: "0 auto",
  },


  title: {
    marginBottom: "5px",
  },


  subtitle: {
    color: "#666",
    marginTop: "0",
  },


  card: {
    background: "#fff",
    border: "1px solid #ddd",
    borderRadius: "12px",
    padding: "25px",
    marginTop: "25px",
    boxShadow:
      "0 2px 8px rgba(0,0,0,0.05)",
  },


  label: {
    display: "block",
    fontWeight: "bold",
    marginTop: "15px",
    marginBottom: "7px",
  },


  input: {
    width: "100%",
    padding: "12px",
    boxSizing: "border-box",
    border: "1px solid #ccc",
    borderRadius: "7px",
    fontSize: "16px",
  },


  textarea: {
    width: "100%",
    minHeight: "100px",
    padding: "12px",
    boxSizing: "border-box",
    border: "1px solid #ccc",
    borderRadius: "7px",
    fontSize: "16px",
    resize: "vertical",
  },


  button: {
    marginTop: "20px",
    padding: "12px 20px",
    border: "none",
    borderRadius: "7px",
    cursor: "pointer",
    fontSize: "16px",
  },


  instagramButton: {
    padding: "12px 20px",
    border: "none",
    borderRadius: "7px",
    cursor: "pointer",
    fontSize: "16px",
  },

  authToggleRow: {
    display: "flex",
    gap: "10px",
    marginBottom: "10px",
  },

  authToggle: {
    flex: 1,
    padding: "10px 12px",
    border: "1px solid #ccc",
    borderRadius: "8px",
    background: "#f7f7f7",
    cursor: "pointer",
  },

  authToggleActive: {
    background: "#eaf2ff",
    borderColor: "#7aa8ff",
  },

  authMessage: {
    color: "#b42318",
    marginTop: "12px",
    fontWeight: "bold",
  },

  connected: {
    fontWeight: "bold",
  },


  campaign: {
    border: "1px solid #eee",
    padding: "18px",
    marginTop: "12px",
    borderRadius: "8px",
  },


  deleteButton: {
    marginTop: "10px",
    padding: "8px 14px",
    border: "none",
    borderRadius: "6px",
    cursor: "pointer",
  },
};


export default App;