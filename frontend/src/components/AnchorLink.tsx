// Taken from https://github.com/grommet/grommet/issues/3572#issuecomment-575887940
import { Anchor, AnchorProps } from "grommet/components/Anchor";
import React from "react";
import { Link, LinkProps } from "react-router-dom";

export const AnchorLink: React.FC<AnchorLinkProps> = (props) => {
  return (
    <Anchor
      as={({ colorProp, hasIcon, hasLabel, focus, ...p }) => <Link {...p} />}
      {...props}
    />
  );
};

export type AnchorLinkProps = LinkProps &
  AnchorProps &
  Omit<JSX.IntrinsicElements["a"], "color">;