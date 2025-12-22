import { Link as HeroLink, LinkProps as HeroLinkProps } from '@heroui/react';
import { createLink } from '@tanstack/react-router';
import React from 'react';

const LinkWrapper = React.forwardRef<HTMLAnchorElement, HeroLinkProps>((props, ref) => {
  return <HeroLink {...props} ref={ref} />;
});

export const Link = createLink(LinkWrapper);
