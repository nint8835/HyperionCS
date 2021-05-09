import { Box, grommet, Grommet, Header, Main, Menu, Text } from "grommet";
import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import { AnchorLink } from "./components/AnchorLink";
import Index from "./pages/Index";

type User = {
  id: string;
  username: string;
  avatar: string | null;
  discriminator: string;
  public_flags: number;
  flags: number;
  locale: string;
  mfa_enabled: boolean;
  premium_type: number;
  email: string;
  verified: boolean;
};

function App() {
  const [user, setUser] = useState<undefined | null | User>(undefined);
  useEffect(() => {
    (async () => {
      const newUser = await fetch("/users/me");
      if (newUser.status == 200) {
        setUser(await newUser.json());
      } else {
        setUser(null);
      }
    })();
  }, [setUser]);
  return (
    <Grommet full theme={grommet} themeMode="dark">
      <Router>
        <Box fill="vertical">
          <Header background="brand" pad="small" justify="between">
            <Text size="medium">
              <AnchorLink
                to="/"
                label="Hyperion Currency System"
                color="light-1"
              />
            </Text>
            <Box>
              {user ? (
                <Menu
                  label={user.username}
                  items={[
                    {
                      label: "Logout",
                      onClick: () => {
                        window.location.pathname = "/logout";
                      },
                    },
                  ]}
                />
              ) : (
                <Menu
                  label="Not logged in"
                  items={[
                    {
                      label: "Login",
                      onClick: () => {
                        window.location.pathname = "/login";
                      },
                    },
                  ]}
                />
              )}
            </Box>
          </Header>
          <Main pad="medium" fill={false} flex={true}>
            <Switch>
              <Route path="/">
                <Index />
              </Route>
            </Switch>
          </Main>
        </Box>
      </Router>
    </Grommet>
  );
}

export default App;
