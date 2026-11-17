import { Link as HeroLink, type LinkProps as HeroLinkProps, buttonVariants } from '@heroui/react';
import { createLink } from '@tanstack/react-router';
import React from 'react';

const LinkWrapper = React.forwardRef<HTMLAnchorElement, HeroLinkProps>((props, ref) => {
  return <HeroLink {...props} ref={ref} />;
});

export const Link = createLink(LinkWrapper);

const ButtonLinkWrapper = React.forwardRef<HTMLAnchorElement, React.ComponentPropsWithoutRef<'a'>>(
  ({ className, ...props }, ref) => <a {...props} ref={ref} className={buttonVariants({ className })} />,
);

export const ButtonLink = createLink(ButtonLinkWrapper);
